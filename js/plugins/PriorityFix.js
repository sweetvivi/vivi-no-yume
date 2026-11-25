// PriorityFix.js Ver.1.2.0
// MIT License (C) 2023 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Modify display priority.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/501856942.html
* @help Ver.1.2.0
*
* @param shiftY
* @text Shift Y
* @desc Fine-tune the character's Y coordinate.
* Disable with 0.
* @type number
* @default 0
* @min -999999
*
* @param useOffsetHeight
* @text Use Offset Height
* @desc this.setOffsetHeight(number of pixels) corrects the display priority based on height.
* @type boolean
* @default true
*
* @param applyToCoordinates
* @text Apply to Coordinates
* @desc Reflects height to Y coordinate.
* @type boolean
* @default true
*
* @param applyToBushDepth
* @text Apply to Bush Depth
* @desc Reflect height to bush depth.
* @type boolean
* @default true
*
* @command setOffsetHeight
* @text Set Offset Height
* @desc  Corrects the display priority based on height.
* @arg characterId
* @text キャラクターID
* @default -1
* @arg height
* @text Height
* @default 0
*
*/

/*:ja
* @target MZ
* @plugindesc 表示優先度を修正します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/501856942.html
* @help
* [更新履歴]
* 2023/12/24：Ver.1.0.0　公開。
* 2023/12/27：Ver.1.1.0　キャラクターのY座標を微調整する機能を追加。
* 2024/02/06：Ver.1.1.1　高さ補正を追加。
* 2024/02/17：Ver.1.1.2　ジャンプ高さを茂み高さに反映する機能を追加。
* 2025/02/10：Ver.1.2.0　茂み高さの算出を修正。
*
* @param shiftY
* @text シフトY
* @desc キャラクターのY座標を微調整します。
* 0で無効化。
* @type number
* @default 0
* @min -999999
*
* @param useOffsetHeight
* @text 高さ補正を使用する
* @desc this.setOffsetHeight(ピクセル数)で高さによる表示優先度の補正を行います。
* @type boolean
* @default true
*
* @param applyToCoordinates
* @text 座標に適用
* @desc 高さをY座標に反映します。
* @type boolean
* @default true
*
* @param applyToBushDepth
* @text 茂み深さに適用
* @desc 高さを茂み深さに反映します。
* @type boolean
* @default true
*
* @command setOffsetHeight
* @text 高さの設定
* @desc 高さによる表示優先度の補正を行います。
* @arg characterId
* @text キャラクターID
* @default -1
* @arg height
* @text 高さ
* @default 0
*
*/

'use strict';
{
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const parameters = PluginManager.parameters(pluginName);
	const shiftY = Number(parameters.shiftY || 0);
	const useOffsetHeight = parameters.useOffsetHeight === "true";
	const applyToCoordinates = useOffsetHeight && parameters.applyToCoordinates === "true";
	const applyToBushDepth = useOffsetHeight && parameters.applyToBushDepth === "true";

	PluginManager.registerCommand(pluginName, "setOffsetHeight", function(args) {
		const character = this.character(+args.characterId);
		if (character) {
			character.setOffsetHeight(+args.height);
		}
	});

	if (window.PluginManagerEx) {
		PluginManagerEx.registerCommand(document.currentScript, "setOffsetHeight", function(args) {
			const character = this.character(args.characterId);
			if (character) {
				character.setOffsetHeight(args.height);
			}
		});
	}

	//-----------------------------------------------------------------------------
	// Game_CharacterBase

	if (useOffsetHeight) {
		const _Game_CharacterBase_initMembers = Game_CharacterBase.prototype.initMembers;
		Game_CharacterBase.prototype.initMembers = function() {
			_Game_CharacterBase_initMembers.call(this);
			this._offsetHeight = 0;
		};

		Game_CharacterBase.prototype.setOffsetHeight = function(height) {
			this._offsetHeight = height;
		};
	}

	if (shiftY) {
		const _Game_CharacterBase_shiftY = Game_CharacterBase.prototype.shiftY;
		Game_CharacterBase.prototype.shiftY = function() {
			const baseY = _Game_CharacterBase_shiftY.call(this);
			return this.isObjectCharacter() ? baseY : baseY + shiftY;
		};
	}

	if (applyToBushDepth) {
		const _Game_CharacterBase_bushDepth = Game_CharacterBase.prototype.bushDepth;
		Game_CharacterBase.prototype.bushDepth = function() {
			let bushDepth = _Game_CharacterBase_bushDepth.call(this) - this._offsetHeight;
			if (this.isJumping()) {
				bushDepth -= this.jumpHeight();
			}
			return bushDepth;
		};
	}

	//-----------------------------------------------------------------------------
	// Sprite_Character

	if (applyToCoordinates) {
		const _Sprite_Character_updatePosition = Sprite_Character.prototype.updatePosition;
		Sprite_Character.prototype.updatePosition = function() {
			_Sprite_Character_updatePosition.call(this);
			if (this._character._offsetHeight) {
				this.y -= this._character._offsetHeight;
			}
		};
	}

	Sprite_Character.prototype.jumpHeight = function() {
		let y = 0;
		if (this._character.isJumping()) {
			y += this._character.jumpHeight();
		}
		return y;
	};

	if (useOffsetHeight) {
		Sprite_Character.prototype.jumpHeight = function() {
			let y = 0;
			if (this._character.isJumping()) {
				y += this._character.jumpHeight();
			}
			if (this._character._offsetHeight) {
				y += this._character._offsetHeight;
			}
			return y;
		};
	}

	if (applyToBushDepth) {
		const _Sprite_Character_updateOther = Sprite_Character.prototype.updateOther;
		Sprite_Character.prototype.updateOther = function() {
			_Sprite_Character_updateOther.call(this);
			if (this._bushDepth > 0) {
				this._bushDepth = Math.min(this.patternHeight(), Math.floor(this._bushDepth*1/this.scale.y));
			}
		};
	}

	//-----------------------------------------------------------------------------
	// Tilemap

	const _Tilemap__compareChildOrder = Tilemap.prototype._compareChildOrder;
	Tilemap.prototype._compareChildOrder = function(a, b) {
		const ay = a.y;
		const by = b.y;
		a.y += a.jumpHeight ? a.jumpHeight() : 0;
		b.y += b.jumpHeight ? b.jumpHeight() : 0;
		const result = _Tilemap__compareChildOrder.call(this, a, b);
		a.y = ay;
		b.y = by;
		return result;
	};
}