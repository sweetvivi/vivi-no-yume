// FasterBattle.js Ver.2.1.0
// MIT License (C) 2023 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ MV
* @plugindesc Speed up battle.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/498870606.html
* @help Ver.2.1.0
* Battle speed will be slightly faster.
* Probably more modest than the existing ones.
*
* @param animationSpeedup
* @text Animation Speedup
* @desc Reduces animation playback time to 80% during acceleration.
* @type boolean
* @default true
*
* @param waitSettings
* @text Wait Settings
* @desc The animation is considered to have finished at the specified number of frames.
* @type struct<waitSetting>[]
*
*/

/*:ja
* @target MZ MV
* @plugindesc 戦闘を高速化します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/498870606.html
* @help 戦闘スピードが若干早くなります。
* たぶん既存のものより控えめです。
*
* [更新履歴]
* 2023/04/03：Ver.1.0.0　公開
* 2023/11/02：Ver.2.0.0　アニメーションを高速化する機能を追加。
* 2023/11/17：Ver.2.0.1　連続攻撃が速すぎたので高速化を緩和。
* 2026/02/16：Ver.2.1.0　アニメーションのウェイト設定を追加。
*
* @param animationSpeedup
* @text アニメーション高速化
* @desc 高速化中にアニメーションの再生時間を80%に短縮します。
* @type boolean
* @default true
*
* @param waitSettings
* @text ウェイト設定
* @desc 指定したフレーム数でアニメーションが終了したとみなされます。
* アニメーションは消えませんが戦闘が進行します。
* @type struct<waitSetting>[]
*
*/

/*~struct~waitSetting:
* @param animationId
* @text Animation ID
* @desc Specify the animation(s).
* For multiple entries, use ",", "-", or "to".
* @type animation
* @default 1
*
* @param frameIndex
* @text Frame Index
* @desc For MV-compatible data, enter the number of frames in the animation editor instead of the actual time.
* @type number
* @default 16
*/

/*~struct~waitSetting:ja
* @param animationId
* @text アニメーションID
* @desc アニメーションを指定します。
* 範囲・複数指定はコンマやハイフン、to(例：1-3,12,15,18to20)
* @type animation
* @default 1
*
* @param frameIndex
* @text フレーム数
* @desc MV互換データの場合は実際の時間ではなくアニメーションエディタのフレーム数を入力してください。
* @type number
* @default 16
*/

'use strict';

{
	const useMZ = Utils.RPGMAKER_NAME === "MZ";
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const parameters = PluginManager.parameters(pluginName);
	const animationSpeedup = parameters["animationSpeedup"] === "true";
	const actorSpeedup = parameters["actorSpeedup"] === "true";
	const waitSettings = {};

	JSON.parse(parameters["waitSettings"] || "[]").forEach(s => {
		const o = JSON.parse(s);
		for (const id of extractIds(o.animationId)) {
			waitSettings[id] = +o.frameIndex;
		}
	});

	function extractIds(str) {
		const ids = [];
		String(str).split(",").forEach(id => {
			if (!isNaN(id)) {
				ids.push(Number(id));
				return;
			}
			const range = id.replace(/to/gi,"-").split("-").map(Number);
			if (isNaN(range[1])) {
				range[1] = range[0];
			}
			for (let i = range[0]; i <= range[1]; i++) {
				ids.push(i);
			}
		});
		return ids;
	}

	//-----------------------------------------------------------------------------
	// Sprite_Animation

	if (useMZ) {
		const _Sprite_Animation_initMembers = Sprite_Animation.prototype.initMembers;
		Sprite_Animation.prototype.initMembers = function() {
			_Sprite_Animation_initMembers.call(this);
			this._activeFrameIndex = 0;
		};

		Sprite_Animation.prototype.setActiveFrameIndex = function(index) {
			this._activeFrameIndex = index;
		};

		Sprite_Animation.prototype.isActive = function() {
			return !this._activeFrameIndex || this._frameIndex < this._activeFrameIndex;
		};
	}

	//-----------------------------------------------------------------------------
	// Sprite_AnimationMV

	const _Sprite_AnimationMV = useMZ ? Sprite_AnimationMV : Sprite_Animation;
	const _Sprite_AnimationMV_initMembers = _Sprite_AnimationMV.prototype.initMembers;
	_Sprite_AnimationMV.prototype.initMembers = function() {
		_Sprite_AnimationMV_initMembers.call(this);
		this._activeFrameIndex = 0;
	};

	_Sprite_AnimationMV.prototype.setActiveFrameIndex = function(index) {
		this._activeFrameIndex = index;
	};

	_Sprite_AnimationMV.prototype.isActive = function() {
		return !this._activeFrameIndex || this.currentFrameIndex() < this._activeFrameIndex -1;
	};

	//-----------------------------------------------------------------------------
	// Spriteset_Battle

	if (useMZ) {
		Spriteset_Battle.prototype.animationBaseDelay = function() {
			return $gameSystem.isSideView() ? Spriteset_Base.prototype.animationBaseDelay.call(this) : 0;
		};

		const _Spriteset_Battle_animationNextDelay = Spriteset_Battle.prototype.animationNextDelay;
		Spriteset_Battle.prototype.animationNextDelay = function() {
			const delay = _Spriteset_Battle_animationNextDelay.call(this);
			return BattleManager._logWindow.isFastForward() ? Math.floor(delay / 2) : delay;
		};
	}

	if (Object.keys(waitSettings).length) {
		if (useMZ) {
			Spriteset_Battle.prototype.isAnimationPlaying = function() {
				return this._animationSprites.some(sprite => sprite.isActive());
			};
		} else {
			Spriteset_Battle.prototype.isAnimationPlaying = function() {
				return this.battlerSprites().some(sprite => sprite._animationSprites.some(sprite => sprite.isActive()));
			};
		}
	}

	const _Spriteset_Battle_isEffecting = Spriteset_Battle.prototype.isEffecting;
	Spriteset_Battle.prototype.isEffecting = function() {
		return BattleManager._logWindow.isFastForward() ? false : _Spriteset_Battle_isEffecting.call(this);
	};

	const _Spriteset_Battle_isAnyoneMoving = Spriteset_Battle.prototype.isAnyoneMoving;
	Spriteset_Battle.prototype.isAnyoneMoving = function() {
		return BattleManager._logWindow.isFastForward() ? false : _Spriteset_Battle_isAnyoneMoving.call(this);
	};

	Spriteset_Battle.prototype.isBusy = function() {
		return BattleManager._logWindow.isFastForward() ? false : this.isAnimationPlaying();
	};

	const animationRate = animationSpeedup ? 0.8 : 1;
	const customAnimation = Object.keys(waitSettings).length || animationRate < 1;
	if (useMZ && customAnimation) {
		const _Spriteset_Battle_createAnimationSprite = Spriteset_Battle.prototype.createAnimationSprite;
		Spriteset_Battle.prototype.createAnimationSprite = function(targets, animation, mirror, delay) {
			_Spriteset_Battle_createAnimationSprite.apply(this, arguments);
			const sprite = this.lastAnimationSprite();
			const activeFrameIndex = waitSettings[animation.id] || 0;
			if (animationRate === 1 || !(BattleManager._logWindow && BattleManager._logWindow.isFastForward())) {
				sprite.setActiveFrameIndex(activeFrameIndex);
				return;
			}
			if (this.isMVAnimation(animation)) {
				sprite._rate = Math.floor(sprite._rate * animationRate) || 1;
				sprite.setupDuration();
				sprite.setActiveFrameIndex(activeFrameIndex);
			} else {
				animation = JsonEx.makeDeepCopy(animation);
				animation.speed = Math.floor(animation.speed / animationRate);
				animation.flashTimings.forEach(timing => timing.frame = Math.floor(timing.frame * animationRate));
				if (animation.timings) {
					animation.timings.forEach(timing => timing.frame = Math.floor(timing.frame * animationRate));
				}
				animation.soundTimings.forEach(timing => timing.frame = Math.floor(timing.frame * animationRate));
				sprite._maxTimingFrames = 0;
				sprite.setup(sprite._targets, animation, sprite._mirror, sprite._delay, sprite._previous);
				sprite.setActiveFrameIndex(Math.floor(activeFrameIndex * animationRate));
			}
		};
	}

	//-----------------------------------------------------------------------------
	// Sprite_Battler

	if (!useMZ && customAnimation) {
		const _Sprite_Battler_startAnimation = Sprite_Battler.prototype.startAnimation;
		Sprite_Battler.prototype.startAnimation = function(animation, mirror, delay) {
			_Sprite_Battler_startAnimation.apply(this, arguments);
			const sprite = this._animationSprites[this._animationSprites.length - 1];
			if (animationRate < 1 && BattleManager._logWindow && BattleManager._logWindow.isFastForward()) {
				sprite._rate = Math.floor(sprite._rate * animationRate) || 1;
				sprite.setupDuration();
			}
			sprite.setActiveFrameIndex(waitSettings[animation.id] || 0);
		};
	}

	//-----------------------------------------------------------------------------
	// Window_BattleLog

	Window_BattleLog.prototype.messageSpeed = function() {
		return 10;
	};

	if (!useMZ) {
		const _Window_BattleLog_animationBaseDelay = Window_BattleLog.prototype.animationBaseDelay;
		Window_BattleLog.prototype.animationBaseDelay = function() {
			return $gameSystem.isSideView() ? _Window_BattleLog_animationBaseDelay.call(this) : 0;
		};

		const _Window_BattleLog_animationNextDelay = Window_BattleLog.prototype.animationNextDelay;
		Window_BattleLog.prototype.animationNextDelay = function() {
			const delay = _Window_BattleLog_animationNextDelay.call(this)
			return this.isFastForward() ? Math.floor(delay / 2) : delay;
		};
	}
}