/*:
 * @target MZ
 * @plugindesc AE86 核心系统：形态切换、束缚、QTE、色情条
 * @author AE86
 * @help
 * ==========================================================================
 * AE86 核心系统
 * ==========================================================================
 *
 * 技能 / 物品注释标签
 * --------------------------------------------------------------------------
 *   <grab>        命中薇薇 → 触发 QTE（回避判定）
 *   <lewd:N>      命中薇薇 → 色情条 +N
 *   <restraint:N> 命中薇薇 → 束缚等级直接设为 N
 *   <selfunbind>  自己脱缚 → 触发高速 QTE，成功束缚 -1
 *   <assist>      队友辅助解缚 → 下一次自己脱缚 QTE 的判定区间 +10px
 *   <unbindall>   万能钥匙 → 解除全部束缚
 *   <cleanse>     净化 → 战斗内只解异常状态，不解祝化
 *
 * 文案标签（都可选，不写就用默认）
 * --------------------------------------------------------------------------
 *   <okmsg:……>     QTE 成功（回避）时显示
 *   <fail1:……>     QTE 失败、束缚升到 Lv1（手）时显示
 *   <fail2:……>     同上，Lv2（腿）
 *   <fail3:……>     同上，Lv3（嘴）
 *   <fail4:……>     同上，Lv4（眼）
 *   <fail5:……>     同上，Lv5（完全束缚）
 *   <unbindok:……>  自脱缚成功
 *   <unbindfail:……> 自脱缚失败
 *
 * 默认文案
 * --------------------------------------------------------------------------
 *   okmsg     → 「薇薇 回避了这次攻击。」
 *   fail1..5  → 「薇薇 的手/腿/嘴/眼睛 被……！」「薇薇 被彻底束缚住了……」
 *   unbindok  → 「薇薇 挣开了一层束缚。」
 *   unbindfail→ 「薇薇 没能挣脱，束缚还在。」
 *
 * 注意：技能 message1 是「发起攻击的提示」，命中与否都会显示。
 *       回避 / 被束缚的文案由 QTE 判定后追加。
 *
 * 状态 ID
 * --------------------------------------------------------------------------
 *    4 魔剑士形态（3 回合）   5 束缚·手   6 束缚·腿   7 束缚·口
 *    8 束缚·目               9 被抓      10 发情      11 敏感
 *   12 媚药                 13 高潮      14 祝化      15 祝化·深
 *
 * 变量
 * --------------------------------------------------------------------------
 *   10 = 色情条（0-100）
 *   11 = 束缚等级（0-5）
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
 * QTE 判定区间
 * --------------------------------------------------------------------------
 *   法师 96px / 魔剑士 150px
 *   色情条每 1 点 −0.5px
 *   束缚每级 −14px
 *   队友辅助 +10px
 *   下限 10px（能看见，但极短）
 *
 * QTE 速度
 * --------------------------------------------------------------------------
 *   被抓（grab）    ：基础 7 + 色情条×0.06 + 束缚×1.5
 *   自己脱缚        ：上式的 2~5 倍（束缚 Lv1=2x，Lv5=5x）
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

        // 终章·观者（致敬杀戮尖塔的姿态机制）
        watcher: {
            enemyId: 9,
            stateWrath: 16,
            stateDivinity: 17,
            varMantra: 12,
            mantraPerTurn: 2,
            mantraMax: 10,
            wrathFromTurn: 2,
        },

        qte: {
            barW: 480,
            barH: 26,
            barY: 404,
            baseZone: 96,
            swordZone: 150,
            minZone: 10,
            zonePerLewd: 0.5,
            zonePerRestraint: 14,
            assistBonus: 10,
            frames: 180,
            baseSpeed: 7,
            speedPerLewd: 0.06,
            speedPerRestraint: 1.5,
            selfMulMin: 2,
            selfMulMax: 5,
        },
    };

    const AE86 = {
        qte: null,
        pendingQte: null, // { mode: 'grab' | 'selfunbind' }
        assistBonus: 0,
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

        reset() {
            this.qte = null;
            this.pendingQte = null;
            this.assistBonus = 0;
            $gameVariables.setValue(CFG.varLewd, 0);
            $gameVariables.setValue(CFG.watcher.varMantra, 0);
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
                if (n < CFG.restraintMax && a.isStateAffected(CFG.stateGrab)) {
                    a.removeState(CFG.stateGrab);
                }
                if (n >= CFG.restraintMax && a.isAlive()) {
                    a.setHp(0);
                }
            }
            if (!silent) this._hudDirty = true;
        },

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

        zoneWidth(assist) {
            const a = this.actor();
            const sword = a && a.isStateAffected(CFG.stateForm);
            const q = CFG.qte;
            let w = sword ? q.swordZone : q.baseZone;
            w -= this.lewd() * q.zonePerLewd;
            w -= this.restraint() * q.zonePerRestraint;
            if (assist) w += q.assistBonus;
            return Math.max(q.minZone, Math.round(w));
        },

        /** 自脱缚速度倍率：束缚 Lv1 = 2 倍，Lv5 = 5 倍 */
        selfUnbindMultiplier() {
            const lv = Math.max(1, this.restraint());
            const q = CFG.qte;
            const t = (lv - 1) / (CFG.restraintMax - 1);
            return q.selfMulMin + (q.selfMulMax - q.selfMulMin) * t;
        },

        markerSpeed(mode) {
            const q = CFG.qte;
            let speed =
                q.baseSpeed +
                this.lewd() * q.speedPerLewd +
                this.restraint() * q.speedPerRestraint;
            if (mode === "selfunbind") speed *= this.selfUnbindMultiplier();
            return speed;
        },

        startQte(mode, meta) {
            mode = mode || "grab";
            const a = this.actor();
            if (!a || !a.isAlive()) return;
            const assist = mode === "selfunbind" && this.assistBonus > 0;
            this.qte = {
                mode,
                meta: meta || {},
                assist,
                pos: 0,
                dir: 1,
                frames: 0,
                limit: CFG.qte.frames,
                zone: this.zoneWidth(assist),
                speed: this.markerSpeed(mode),
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

        /** 失败时按新束缚等级取文案：<fail1> 手 / <fail2> 腿 / <fail3> 嘴 / <fail4> 眼 / <fail5> 完全 */
        failMessage(meta, level) {
            const key = "fail" + Math.min(level, CFG.restraintMax);
            if (meta && meta[key]) return meta[key];
            const name = this.actor() ? this.actor().name() : "薇薇";
            const fallback = {
                1: `${name} 的手被束缚住了！`,
                2: `${name} 的腿被束缚住了！`,
                3: `${name} 的嘴被堵上了，无法吟唱！`,
                4: `${name} 的眼睛被遮住了！`,
                5: `${name} 被彻底束缚住了……`,
            };
            return fallback[Math.min(level, CFG.restraintMax)];
        },

        judgeQte(success) {
            const q = this.qte;
            if (!q) return;
            this.qte = null;
            this._hudDirty = true;
            const a = this.actor();
            const meta = q.meta || {};
            const name = a ? a.name() : "薇薇";

            if (q.mode === "selfunbind") {
                this.assistBonus = 0;
                if (success) {
                    this.setRestraint(this.restraint() - 1);
                    this.log(meta.unbindok || `${name} 挣开了一层束缚。`);
                } else {
                    this.log(meta.unbindfail || `${name} 没能挣脱，束缚还在。`);
                }
                return;
            }

            // grab：成功 = 回避，失败 = 束缚等级 +1
            if (success) {
                if (a && a.isStateAffected(CFG.stateGrab)) a.removeState(CFG.stateGrab);
                if (a) a.gainTp(20);
                this.log(meta.okmsg || `${name} 回避了这次攻击。`);
            } else {
                const next = Math.min(this.restraint() + 1, CFG.restraintMax);
                this.setRestraint(next);
                this.log(this.failMessage(meta, next));
            }
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

        // ---------------- 终章·观者 ----------------

        watcherEnemy() {
            const c = CFG.watcher;
            return $gameTroop.members().find((e) => e.enemyId() === c.enemyId) || null;
        },

        mantra() {
            return $gameVariables.value(CFG.watcher.varMantra) || 0;
        },

        setMantra(n) {
            $gameVariables.setValue(CFG.watcher.varMantra, Math.max(0, Math.floor(n)));
            this._hudDirty = true;
        },

        /** 观者当前姿态：'none' | 'wrath' | 'divinity' */
        watcherStance() {
            const w = this.watcherEnemy();
            if (!w || !w.isAlive()) return "none";
            const c = CFG.watcher;
            if (w.isStateAffected(c.stateDivinity)) return "divinity";
            if (w.isStateAffected(c.stateWrath)) return "wrath";
            return "none";
        },

        /** 每回合开始：累积真言，满了进神格，否则维持愤怒 */
        updateWatcherTurn() {
            const c = CFG.watcher;
            const w = this.watcherEnemy();
            if (!w || !w.isAlive()) return;

            // 已在本回合神格里，跳过累积
            if (w.isStateAffected(c.stateDivinity)) {
                this._hudDirty = true;
                return;
            }

            const turn = $gameTroop.turnCount();
            const next = this.mantra() + c.mantraPerTurn;
            this.setMantra(next);

            if (next >= c.mantraMax) {
                this.setMantra(0);
                w.addState(c.stateDivinity);
                if (w.isStateAffected(c.stateWrath)) w.removeState(c.stateWrath);
                this.log("观者攒满了真言，遁入神格。");
            } else if (turn >= c.wrathFromTurn && !w.isStateAffected(c.stateWrath)) {
                w.addState(c.stateWrath);
                this.log("观者的气息变了——愤怒。");
            }
            this._hudDirty = true;
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

            if (this.assistBonus > 0) {
                bmp.fontSize = 18;
                bmp.textColor = "#9fe6b0";
                bmp.drawText("队友已就位（区间 +10）", right - 300, 92, 300, 24, "right");
            }

            this.drawWatcherHud(bmp);
        },

        /** 左上角：观者的姿态与真言（紫调，致敬杀戮尖塔） */
        drawWatcherHud(bmp) {
            const w = this.watcherEnemy();
            if (!w || !w.isAlive()) return;
            const c = CFG.watcher;
            const stance = this.watcherStance();

            const x = 20;
            const y = 10;
            bmp.fontFace = $gameSystem.mainFontFace();

            // 底板
            bmp.fillRect(x - 8, y - 6, 250, 76, "rgba(28,16,44,0.72)");
            bmp.fillRect(x - 8, y - 6, 250, 2, "#a06ed8");
            bmp.fillRect(x - 8, y + 68, 250, 2, "#a06ed8");

            bmp.fontSize = 20;
            bmp.outlineColor = "rgba(0,0,0,0.85)";
            bmp.outlineWidth = 4;

            const label = {
                none: "无姿态",
                wrath: "愤怒",
                divinity: "神格",
            }[stance];
            const color = {
                none: "#c9b6e8",
                wrath: "#e0705a",
                divinity: "#f2d06b",
            }[stance];

            bmp.textColor = "#c9b6e8";
            bmp.drawText("观者", x, y, 90, 26);
            bmp.textColor = color;
            bmp.drawText(label, x + 60, y, 120, 26);

            if (stance === "wrath") {
                bmp.fontSize = 15;
                bmp.textColor = "#e0a090";
                bmp.drawText("伤害×2 / 受伤×2", x, y + 22, 230, 20);
            } else if (stance === "divinity") {
                bmp.fontSize = 15;
                bmp.textColor = "#f2d06b";
                bmp.drawText("伤害×3", x, y + 22, 230, 20);
            } else {
                bmp.fontSize = 15;
                bmp.textColor = "#9a86b8";
                bmp.drawText("评估中", x, y + 22, 230, 20);
            }

            // 真言条
            const m = this.mantra();
            const barW = 200;
            const barX = x;
            const barY = y + 44;
            bmp.fillRect(barX, barY, barW, 10, "rgba(0,0,0,0.6)");
            const fill = Math.round((barW * m) / c.mantraMax);
            if (fill > 0) bmp.fillRect(barX, barY, fill, 10, "#a06ed8");
            bmp.fontSize = 14;
            bmp.textColor = "#c9b6e8";
            bmp.outlineWidth = 3;
            bmp.drawText(`真言 ${m}/${c.mantraMax}`, barX + barW + 6, barY - 4, 90, 20);
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

            // 判定区间：区间很小时画成一排小竖条，保证看得见
            const zx = x + W / 2 - q.zone / 2;
            const zoneColor = blind
                ? "rgba(90,200,120,0.25)"
                : q.mode === "selfunbind"
                  ? "#e0a53f"
                  : "#3fae6a";
            if (q.zone <= 24) {
                const step = q.zone / 4;
                for (let i = 0; i < 4; i++) {
                    bmp.fillRect(zx + i * step, y + 3, Math.max(1, step - 2), H - 6, zoneColor);
                }
            } else {
                bmp.fillRect(zx, y, q.zone, H, zoneColor);
            }

            bmp.fillRect(x, y, W, 2, "#ffffff");
            bmp.fillRect(x, y + H - 2, W, 2, "#ffffff");

            const mx = x + q.pos;
            bmp.fillRect(mx - 3, y - 6, 6, H + 12, blind ? "rgba(255,255,255,0.22)" : "#ffe066");

            bmp.fontSize = 20;
            bmp.textColor = "#ffffff";
            bmp.outlineColor = "rgba(0,0,0,0.85)";
            bmp.outlineWidth = 4;
            let hint;
            if (blind) {
                hint = "视线被遮住了……";
            } else if (q.mode === "selfunbind") {
                hint = q.assist ? "队友帮忙——按 OK 挣脱！" : "自己挣脱——按 OK！";
            } else {
                hint = "按 OK 挣脱！";
            }
            bmp.drawText(hint, x, y - 44, W, 30, "center");
        },
    };

    window.AE86 = AE86;

    // ------------------------------------------------------------------
    // 形态（ATK 倍率）
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
    // 束缚限制
    // ------------------------------------------------------------------

    const _Game_Actor_meetsSkillConditions = Game_Actor.prototype.meetsSkillConditions;
    Game_Actor.prototype.meetsSkillConditions = function (skill) {
        if (!_Game_Actor_meetsSkillConditions.call(this, skill)) return false;
        const meta = (skill && skill.meta) || {};
        const lv = AE86.restraint();

        // 自己脱缚：只有薇薇、且被束缚时才能用
        if (meta.selfunbind) {
            return this.actorId() === CFG.actorId && lv >= 1;
        }
        // 队友辅助：只有别的角色、且薇薇被束缚时才能用
        if (meta.assist) {
            return this.actorId() !== CFG.actorId && lv >= 1;
        }

        if (this.actorId() !== CFG.actorId) return true;
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
        // 万能钥匙任何时候都能用
        if (item.meta && item.meta.unbindall) return true;
        return AE86.restraint() < 1;
    };

    // ------------------------------------------------------------------
    // 女装：只有 note 带 crossdress 的角色能装备 <crossdress> 防具
    // ------------------------------------------------------------------

    const _Game_Actor_canEquipArmor = Game_Actor.prototype.canEquipArmor;
    Game_Actor.prototype.canEquipArmor = function (item) {
        if (!_Game_Actor_canEquipArmor.call(this, item)) return false;
        if (item && item.meta && item.meta.crossdress) {
            const actor = $dataActors[this.actorId()];
            return !!(actor && /crossdress/.test(actor.note || ""));
        }
        return true;
    };

    const _BattleManager_canEscape = BattleManager.canEscape;
    BattleManager.canEscape = function () {
        if (AE86.restraint() >= 2) return false;
        return _BattleManager_canEscape.call(this);
    };

    // ------------------------------------------------------------------
    // 技能 / 物品效果
    // ------------------------------------------------------------------

    const _Game_Action_apply = Game_Action.prototype.apply;
    Game_Action.prototype.apply = function (target) {
        _Game_Action_apply.call(this, target);
        const item = this.item();
        if (!item || !item.meta) return;
        if (!target.isActor || !target.isActor()) return;
        if (target.actorId() !== CFG.actorId) return;
        const meta = item.meta;

        // 万能钥匙：无视命中判定，直接解全部束缚
        if (meta.unbindall) {
            AE86.setRestraint(0);
            return;
        }
        // 队友辅助：给下一次自脱缚 +10px
        if (meta.assist) {
            AE86.assistBonus = CFG.qte.assistBonus;
            AE86._hudDirty = true;
            return;
        }
        if (!target.result().isHit()) return;

        if (meta.grab) AE86.pendingQte = { mode: "grab", meta };
        if (meta.selfunbind) AE86.pendingQte = { mode: "selfunbind", meta };
        if (meta.lewd !== undefined) AE86.addLewd(meta.lewd);
        if (meta.restraint !== undefined) AE86.setRestraint(Number(meta.restraint));
    };

    // 净化：战斗内不允许解除祝化
    const _Game_Action_itemEffectRemoveState = Game_Action.prototype.itemEffectRemoveState;
    Game_Action.prototype.itemEffectRemoveState = function (target, effect) {
        const isCurse = effect.dataId === CFG.stateCurse || effect.dataId === CFG.stateDeepCurse;
        if (isCurse && $gameParty.inBattle()) {
            this.makeFailure(target);
            return;
        }
        _Game_Action_itemEffectRemoveState.call(this, target, effect);
    };

    // ------------------------------------------------------------------
    // 战斗流程
    // ------------------------------------------------------------------

    const _BattleManager_setup = BattleManager.setup;
    BattleManager.setup = function (troopId, canEscape, canLose) {
        _BattleManager_setup.call(this, troopId, canEscape, canLose);
        AE86.reset();
    };

    const _BattleManager_update = BattleManager.update;
    BattleManager.update = function (timeActive) {
        if (AE86.qte) return;
        if (AE86.pendingQte && !this.isBusy()) {
            const { mode, meta } = AE86.pendingQte;
            AE86.pendingQte = null;
            AE86.startQte(mode, meta);
            return;
        }
        _BattleManager_update.call(this, timeActive);
    };

    // ------------------------------------------------------------------
    // 场景（叠加层）
    // ------------------------------------------------------------------

    // ------------------------------------------------------------------
    // 终章·观者：每回合累积真言 / 愤怒时受伤翻倍
    // ------------------------------------------------------------------

    const _BattleManager_startTurn = BattleManager.startTurn;
    BattleManager.startTurn = function () {
        _BattleManager_startTurn.call(this);
        AE86.updateWatcherTurn();
    };

    const _Game_Action_makeDamageValue = Game_Action.prototype.makeDamageValue;
    Game_Action.prototype.makeDamageValue = function (target, critical) {
        let value = _Game_Action_makeDamageValue.call(this, target, critical);
        const c = CFG.watcher;
        if (
            value > 0 &&
            target &&
            typeof target.isEnemy === "function" &&
            target.isEnemy() &&
            typeof target.enemyId === "function" &&
            target.enemyId() === c.enemyId &&
            target.isStateAffected(c.stateWrath)
        ) {
            value = Math.round(value * 2);
        }
        return value;
    };

    // ------------------------------------------------------------------
    // 场景（叠加层）
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
        AE86.pendingQte = null;
        AE86.assistBonus = 0;
        _Scene_Battle_terminate.call(this);
    };
})();
