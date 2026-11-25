/*:
 * @target MZ
 * @plugindesc AE86 核心系统：法师/魔剑士形态切换、束缚、QTE、色情条
 * @author AE86
 * @help
 * ==========================================================================
 * AE86 核心系统
 * ==========================================================================
 *
 * 数据库约定
 * --------------------------------------------------------------------------
 * 技能注释：
 *   <grab>        命中薇薇时触发 QTE；QTE 失败则束缚等级 +1
 *   <lewd:N>      命中薇薇时色情条 +N
 *   <restraint:N> 命中薇薇时把束缚等级直接设为 N
 *
 * 状态 ID：
 *    4 魔剑士形态    5 束缚·手    6 束缚·腿    7 束缚·口    8 束缚·目
 *    9 被抓         10 发情      11 敏感      12 媚药      13 高潮
 *   14 祝化         15 祝化·深
 *
 * 变量：
 *   10 = 色情条（0-100）
 *   11 = 束缚等级（0-5，只读镜像，给事件判断用）
 *
 * 束缚等级效果
 * --------------------------------------------------------------------------
 *   Lv0 自由
 *   Lv1 手被缚   → 不能普攻、不能用道具、不能切换形态
 *   Lv2 腿被缚   → 不能逃跑
 *   Lv3 口被堵   → 不能使用魔法（技能类型 1）
 *   Lv4 目被遮   → QTE 条难以看清
 *   Lv5 完全束缚 → 战败（HP 归零）
 *
 * 形态
 * --------------------------------------------------------------------------
 *   默认法师形态：ATK ×0.35（近战极弱），MAT 正常
 *   魔剑士形态  ：ATK ×2.0
 *   用技能「剑心·转」（消耗 TP）切换
 */

(() => {
    "use strict";

    const CFG = {
        actorId: 1,

        stateForm: 4,
        stateHands: 5,
        stateLegs: 6,
        stateMouth: 7,
        stateEyes: 8,
        stateGrab: 9,
        stateArousal: 10,
        stateSensitive: 11,
        stateAphro: 12,
        stateOrgasm: 13,
        stateCurse: 14,
        stateDeepCurse: 15,

        skillAttack: 1,
        skillFormSwitch: 6,
        magicSkillType: 1,

        varLewd: 10,
        varRestraint: 11,

        lewdMax: 100,
        lewdAfterOrgasm: 30,
        restraintMax: 5,

        atkRateMage: 0.35,
        atkRateSword: 2.0,

        qte: {
            barW: 480,
            barH: 26,
            barY: 404,
            baseZone: 96,
            swordZone: 150,
            minZone: 28,
            frames: 180,
            baseSpeed: 7,
        },
    };

    // ------------------------------------------------------------------
    // 核心对象
    // ------------------------------------------------------------------

    const AE86 = {
        qte: null,
        pendingQte: false,
        _hudDirty: true,

        actor() {
            return $gameActors.actor(CFG.actorId);
        },

        restraint() {
            return $gameVariables.value(CFG.varRestraint) || 0;
        },

        lewd() {
            return $gameVariables.value(CFG.varLewd) || 0;
        },

        /** 战斗开始 / 结束时清空状态 */
        reset() {
            this.qte = null;
            this.pendingQte = false;
            $gameVariables.setValue(CFG.varLewd, 0);
            this.setRestraint(0, true);
            this._hudDirty = true;
        },

        setRestraint(n, silent) {
            n = Math.max(0, Math.min(CFG.restraintMax, Math.floor(n)));
            $gameVariables.setValue(CFG.varRestraint, n);
            const a = this.actor();
            if (a) {
                const table = [
                    [CFG.stateHands, 1],
                    [CFG.stateLegs, 2],
                    [CFG.stateMouth, 3],
                    [CFG.stateEyes, 4],
                ];
                for (const [sid, lv] of table) {
                    if (n >= lv) {
                        if (!a.isStateAffected(sid)) a.addState(sid);
                    } else if (a.isStateAffected(sid)) {
                        a.removeState(sid);
                    }
                }
                if (n >= CFG.restraintMax && a.isAlive()) {
                    a.setHp(0);
                }
            }
            if (!silent) this._hudDirty = true;
        },

        /** 色情条增加；满了触发高潮并回落到 30 */
        addLewd(amount) {
            const a = this.actor();
            if (!a) return;
            let gain = Number(amount) || 0;
            if (a.isStateAffected(CFG.stateArousal)) gain *= 1.5;
            if (a.isStateAffected(CFG.stateSensitive)) gain *= 1.5;
            if (a.isStateAffected(CFG.stateAphro)) gain *= 1.5;
            const v = this.lewd() + gain;
            if (v >= CFG.lewdMax) {
                a.addState(CFG.stateOrgasm);
                $gameVariables.setValue(CFG.varLewd, CFG.lewdAfterOrgasm);
            } else {
                $gameVariables.setValue(CFG.varLewd, Math.round(v));
            }
            this._hudDirty = true;
        },

        // ---------------- QTE ----------------

        zoneWidth() {
            const a = this.actor();
            const sword = a && a.isStateAffected(CFG.stateForm);
            let w = sword ? CFG.qte.swordZone : CFG.qte.baseZone;
            w -= this.lewd() * 0.35;
            w -= this.restraint() * 14;
            return Math.max(CFG.qte.minZone, Math.round(w));
        },

        markerSpeed() {
            return CFG.qte.baseSpeed + this.lewd() * 0.06 + this.restraint() * 1.5;
        },

        startQte() {
            const a = this.actor();
            if (!a || !a.isAlive()) return;
            this.qte = {
                pos: 0,
                dir: 1,
                frames: 0,
                limit: CFG.qte.frames,
                zone: this.zoneWidth(),
                speed: this.markerSpeed(),
            };
            this._hudDirty = true;
        },

        updateQte() {
            const q = this.qte;
            if (!q) return;
            q.frames++;
            q.pos += q.dir * q.speed;
            if (q.pos >= CFG.qte.barW) {
                q.pos = CFG.qte.barW;
                q.dir = -1;
            }
            if (q.pos <= 0) {
                q.pos = 0;
                q.dir = 1;
            }
            this._hudDirty = true;

            if (Input.isTriggered("ok") || TouchInput.isTriggered()) {
                const center = CFG.qte.barW / 2;
                this.judgeQte(Math.abs(q.pos - center) <= q.zone / 2);
                return;
            }
            if (q.frames >= q.limit) {
                this.judgeQte(false);
            }
        },

        judgeQte(success) {
            if (!this.qte) return;
            this.qte = null;
            const a = this.actor();
            if (a && a.isStateAffected(CFG.stateGrab)) a.removeState(CFG.stateGrab);
            if (success) {
                if (a) a.gainTp(20);
                this.log("挣脱了束缚！");
            } else {
                this.setRestraint(this.restraint() + 1);
                this.log("没能挣脱，被缠得更紧了……");
            }
            this._hudDirty = true;
        },

        log(text) {
            const w = BattleManager._logWindow;
            if (w && w.addText) w.addText(text);
        },

        // ---------------- 绘制 ----------------

        updateOverlay(scene) {
            const bmp = scene._ae86Bitmap;
            if (!bmp) return;
            const active = !!this.qte;
            if (active) this.updateQte();
            if (!active && !this._hudDirty) return;
            bmp.clear();
            this.drawHud(bmp);
            if (this.qte) this.drawQte(bmp);
            this._hudDirty = false;
        },

        drawHud(bmp) {
            if (!$gameParty.inBattle()) return;
            const right = Graphics.boxWidth - 20;
            bmp.fontFace = $gameSystem.mainFontFace();
            bmp.fontSize = 22;
            bmp.textColor = "#ffffff";
            bmp.outlineColor = "rgba(0,0,0,0.85)";
            bmp.outlineWidth = 4;

            const lewd = this.lewd();
            const lv = this.restraint();
            bmp.drawText(`色情  ${lewd}/${CFG.lewdMax}`, right - 300, 10, 300, 30, "right");
            bmp.drawText(`束缚  Lv.${lv}`, right - 300, 40, 300, 30, "right");

            const barW = 220;
            const barX = right - barW;
            const barY = 74;
            bmp.fillRect(barX, barY, barW, 12, "rgba(0,0,0,0.65)");
            const fill = Math.round((barW * lewd) / CFG.lewdMax);
            if (fill > 0) bmp.fillRect(barX, barY, fill, 12, "#d2557a");
        },

        drawQte(bmp) {
            const q = this.qte;
            const W = CFG.qte.barW;
            const H = CFG.qte.barH;
            const x = (Graphics.boxWidth - W) / 2;
            const y = CFG.qte.barY;
            const blind = this.restraint() >= 4;

            bmp.fillRect(x - 4, y - 4, W + 8, H + 8, "rgba(0,0,0,0.8)");
            bmp.fillRect(x, y, W, H, "rgba(40,40,48,0.95)");

            const zx = x + W / 2 - q.zone / 2;
            bmp.fillRect(zx, y, q.zone, H, blind ? "rgba(90,200,120,0.22)" : "#3fae6a");

            bmp.fillRect(x, y, W, 2, "#ffffff");
            bmp.fillRect(x, y + H - 2, W, 2, "#ffffff");

            const mx = x + q.pos;
            bmp.fillRect(mx - 3, y - 6, 6, H + 12, blind ? "rgba(255,255,255,0.22)" : "#ffe066");

            bmp.fontSize = 20;
            bmp.textColor = "#ffffff";
            bmp.outlineColor = "rgba(0,0,0,0.85)";
            bmp.outlineWidth = 4;
            const hint = blind ? "视线被遮住了……" : "按 OK 挣脱！";
            bmp.drawText(hint, x, y - 44, W, 30, "center");
        },
    };

    window.AE86 = AE86;

    // ------------------------------------------------------------------
    // 钩子：形态（ATK 倍率）
    // ------------------------------------------------------------------

    const _Game_Actor_param = Game_Actor.prototype.param;
    Game_Actor.prototype.param = function (paramId) {
        const value = _Game_Actor_param.call(this, paramId);
        if (this.actorId() === CFG.actorId && paramId === 2) {
            const rate = this.isStateAffected(CFG.stateForm)
                ? CFG.atkRateSword
                : CFG.atkRateMage;
            return Math.round(value * rate);
        }
        return value;
    };

    // ------------------------------------------------------------------
    // 钩子：束缚限制
    // ------------------------------------------------------------------

    const _Game_Actor_meetsSkillConditions = Game_Actor.prototype.meetsSkillConditions;
    Game_Actor.prototype.meetsSkillConditions = function (skill) {
        if (!_Game_Actor_meetsSkillConditions.call(this, skill)) return false;
        if (this.actorId() !== CFG.actorId) return true;
        const lv = AE86.restraint();
        if (lv >= 1) {
            if (skill.id === CFG.skillAttack) return false;
            if (skill.id === CFG.skillFormSwitch) return false;
        }
        if (lv >= 3 && skill.stypeId === CFG.magicSkillType) return false;
        return true;
    };

    const _Game_Actor_meetsItemConditions = Game_Actor.prototype.meetsItemConditions;
    Game_Actor.prototype.meetsItemConditions = function (item) {
        if (!_Game_Actor_meetsItemConditions.call(this, item)) return false;
        if (this.actorId() !== CFG.actorId) return true;
        return AE86.restraint() < 1;
    };

    const _BattleManager_canEscape = BattleManager.canEscape;
    BattleManager.canEscape = function () {
        if (AE86.restraint() >= 2) return false;
        return _BattleManager_canEscape.call(this);
    };

    // ------------------------------------------------------------------
    // 钩子：技能命中 → QTE / 色情条 / 束缚
    // ------------------------------------------------------------------

    const _Game_Action_apply = Game_Action.prototype.apply;
    Game_Action.prototype.apply = function (target) {
        _Game_Action_apply.call(this, target);
        const item = this.item();
        if (!item || !item.meta) return;
        if (!target.isActor || !target.isActor()) return;
        if (target.actorId() !== CFG.actorId) return;
        if (!target.result().isHit()) return;

        const meta = item.meta;
        if (meta.grab) AE86.pendingQte = true;
        if (meta.lewd !== undefined) AE86.addLewd(meta.lewd);
        if (meta.restraint !== undefined) AE86.setRestraint(Number(meta.restraint));
    };

    // ------------------------------------------------------------------
    // 钩子：战斗流程
    // ------------------------------------------------------------------

    const _BattleManager_setup = BattleManager.setup;
    BattleManager.setup = function (troopId, canEscape, canLose) {
        _BattleManager_setup.call(this, troopId, canEscape, canLose);
        AE86.reset();
    };

    const _BattleManager_update = BattleManager.update;
    BattleManager.update = function (timeActive) {
        if (AE86.qte) return; // QTE 进行中，战斗暂停
        if (AE86.pendingQte && !this.isBusy()) {
            AE86.pendingQte = false;
            AE86.startQte();
            return;
        }
        _BattleManager_update.call(this, timeActive);
    };

    // ------------------------------------------------------------------
    // 钩子：场景（叠加层）
    // ------------------------------------------------------------------

    const _Scene_Battle_create = Scene_Battle.prototype.create;
    Scene_Battle.prototype.create = function () {
        _Scene_Battle_create.call(this);
        this._ae86Bitmap = new Bitmap(Graphics.boxWidth, Graphics.boxHeight);
        this._ae86Sprite = new Sprite(this._ae86Bitmap);
        this.addChild(this._ae86Sprite);
    };

    const _Scene_Battle_update = Scene_Battle.prototype.update;
    Scene_Battle.prototype.update = function () {
        _Scene_Battle_update.call(this);
        AE86.updateOverlay(this);
    };

    const _Scene_Battle_terminate = Scene_Battle.prototype.terminate;
    Scene_Battle.prototype.terminate = function () {
        AE86.qte = null;
        AE86.pendingQte = false;
        _Scene_Battle_terminate.call(this);
    };
})();
