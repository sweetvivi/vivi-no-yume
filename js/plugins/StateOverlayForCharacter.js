// StateOverlayForCharacter.js Ver.1.0.0
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Allows side view state overlays to be displayed on map characters as well.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/512016106.html
* @help Ver.1.0.0
* [Comment]
* Place a comment on the first line of the event contents and enter it in the following format:
* <stateOverlay:n> //Show overlay with index n
* <stateOverlay:8> //Show paralysis overlay
* <stateOverlay:paralysis> //Show paralysis overlay
*
* [Scripts (Movement Route)]
* this.setStateOverlay(n) //Show overlay with index n
* this.setStateOverlay(0) //Erase overlay
* this.setStateOverlay(-1) //Shows party member state overlays (player only)
* this.setStateOverlay(8) //Show paralysis overlay
* this.setStateOverlay("paralysis") //Show paralysis overlay
*
* @param useComments
* @text Use Comments
* @desc Reflects the input contents in the comment to the event.
* @default true
* @type boolean
*
* @param automate
* @text Automate
* @desc Displays an overlay that matches the state of each party member from the start.
* @default false
* @type boolean
*
* @param baseOffsetY
* @text Base Offset Y
* @desc How far to offset the overlay from the character's feet.
* @default 0
*
* @param offsetY
* @text Offset Y
* @desc How far each overlay should be offset from the character's feet.
* @default ["0","0","0","0","0","0","0","12","0","0"]
* @type string[]
*
* @param sizeRatio
* @text Size Ratio
* @desc The ratio of the overlay size to the character.
* The initial value is the ratio of SV actor to overlay.
* @default 1.5
*
* @param minScale
* @text Minimum Scale
* @desc Do not make the overlay any smaller.
* Disabled: 0
* @default 0
*
* @param nameList
* @text Name List
* @desc Set the name for each overlay.
* It can be used as an index in notes and scripts.
* @type string[]
* @default ["Poison","Blind","Silence","Rage","Confusion","Charm","Sleep","Paralysis","Curse","Fear"]
*
* @command setStateOverlay
* @text Set State Overlay
* @desc Shows the state overlay.
* @arg characterId
* @text Character ID
* @desc Player: -1  This Event: 0
* @default -1
* @arg overlay
* @text Overlay
* @desc The parameter [Name List] settings will not be reflected here, so please rewrite this plugin yourself.
* @default 0
* @type select
* @option Current State (Player Only)
* @value -1
* @option None
* @value 0
* @option Poison
* @option Blind
* @option Silence
* @option Rage
* @option Confusion
* @option Charm
* @option Sleep
* @option Paralysis
* @option Curse
* @option Fear
*
*/

/*:ja
* @target MZ
* @plugindesc サイドビューのステート重ね合わせをマップキャラクターにも表示可能にします。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/512016106.html
* @help 
* [注釈]
* イベントの実行内容一行目に注釈を配置し、以下の形式で入力すると反映されます。
* <stateOverlay:n> //インデックスnの重ね合わせを表示
* <stateOverlay:8> //麻痺の重ね合わせを表示
* <stateOverlay:麻痺> //麻痺の重ね合わせを表示
*
* [スクリプト（移動ルート）]
* this.setStateOverlay(n) //インデックスnの重ね合わせを表示
* this.setStateOverlay(0) //重ね合わせを消去
* this.setStateOverlay(-1) //パーティメンバーのステートの重ね合わせを表示（プレイヤーのみ）
* this.setStateOverlay(8) //麻痺の重ね合わせを表示
* this.setStateOverlay("麻痺") //麻痺の重ね合わせを表示
*
* [更新履歴]
* 2025/03/19：Ver.1.0.0　公開。
*
* @param useComments
* @text 注釈を使う
* @desc 注釈の入力内容をイベントに反映します。
* @default true
* @type boolean
*
* @param automate
* @text 自動化する
* @desc 最初からパーティメンバーのステートに合わせた重ね合わせを表示します。
* @default false
* @type boolean
*
* @param baseOffsetY
* @text 基本オフセットY
* @desc 重ね合わせをキャラクターの足元からどれくらいずらすか。
* @default 0
*
* @param offsetY
* @text オフセットY
* @desc それぞれの重ね合わせをキャラクターの足元からどれくらいずらすか。
* @default ["0","0","0","0","0","0","0","12","0","0"]
* @type string[]
*
* @param sizeRatio
* @text サイズ比率
* @desc キャラクターに対する重ね合わせの大きさの比率。
* 初期値はSVアクターと重ね合わせの比率を採用。
* @default 1.5
*
* @param minScale
* @text 最小拡大率
* @desc それ以上重ね合わせを小さくしません。
* 無効化：0
* @default 0
*
* @param nameList
* @text 名前リスト
* @desc それぞれの重ね合わせに対応した名前を設定します。
* メモやスクリプトでインデックス代わりに使えます。
* @type string[]
* @default ["毒","暗闇","沈黙","激昂","混乱","魅了","睡眠","麻痺","呪い","恐怖"]
*
* @command setStateOverlay
* @text ステート重ね合わせの設定
* @desc ステートの重ね合わせを表示します。
* @arg characterId
* @text キャラクターID
* @desc プレイヤー：-1　このイベント：0
* @default -1
* @arg overlay
* @text 重ね合わせ
* @desc パラメータ[名前リスト]の設定はこちらに反映されないので自分でこのプラグインを書き換えて下さい。
* @default 0
* @type select
* @option 現在のステート（プレイヤーのみ）
* @value -1
* @option なし
* @value 0
* @option 毒
* @option 暗闇
* @option 沈黙
* @option 激昂
* @option 混乱
* @option 魅了
* @option 睡眠
* @option 麻痺
* @option 呪い
* @option 恐怖
*
*/

var AWY = AWY || {};
'use strict';
{
	const script = document.currentScript;
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const params = PluginManager.parameters(pluginName);
	const baseOffsetY = Number(params.baseOffsetY || 0);
	const offsetY = JSON.parse(params.offsetY || "[]").map(n => baseOffsetY + Number(n));
	const nameList = JSON.parse(params.nameList || "[]").map(str => str.toLowerCase());
	const sizeRatio = Number(params.sizeRatio || 1);
	const minScale = Number(params.minScale || 1);
	const useComments = params.useComments === "true";
	offsetY.unshift(0);

	function getIndex(index) {
		return index ? (nameList.indexOf(String(index).toLowerCase()) + 1) || Number(index) : 0;
	}

	//-----------------------------------------------------------------------------
	// _PluginManager

	const _pluginName = window.PluginManagerEx ? document.currentScript : pluginName; 
	const _PluginManager = window.PluginManagerEx || window.PluginManager;

	_PluginManager.registerCommand(_pluginName, "setStateOverlay", function(args) {
		const character = this.character(+args.characterId);
		if (character) {
			const min = character === $gamePlayer ? -1 : 0;
			const index = Math.max(getIndex(args.overlay), min);
			character.setStateOverlay(index);
		}
	});

	//-----------------------------------------------------------------------------
	// Game_CharacterBase

	const _Game_CharacterBase_initMembers = Game_CharacterBase.prototype.initMembers;
	Game_CharacterBase.prototype.initMembers = function() {
		_Game_CharacterBase_initMembers.call(this);
		this._stateOverlayIndex = 0;
	};

	Game_CharacterBase.prototype.stateOverlayIndex = function() {
		return this._stateOverlayIndex;
	};

	Game_CharacterBase.prototype.setStateOverlay = function(id) {
		this._stateOverlayIndex = getIndex(id);
	};

	//-----------------------------------------------------------------------------
	// Game_Event

	const _Game_Event_clearPageSettings = Game_Event.prototype.clearPageSettings;
	Game_Event.prototype.clearPageSettings = function() {
		_Game_Event_clearPageSettings.call(this);
		this.setStateOverlay(0);
	};

	if (useComments) {
		const _Game_Event_setupPageSettings = Game_Event.prototype.setupPageSettings;
		Game_Event.prototype.setupPageSettings = function() {
			_Game_Event_setupPageSettings.call(this);
			this.setStateOverlay(this.page().stateOverlay);
		};
	}

	//-----------------------------------------------------------------------------
	// Game_Player

	const _Game_Player_initMembers = Game_Player.prototype.initMembers;
	Game_Player.prototype.initMembers = function() {
		_Game_Player_initMembers.call(this);
		if (params.automate === "true") this._stateOverlayIndex = -1;
	};

	Game_Player.prototype.stateOverlayIndex = function() {
		if (this.isAutoStateOverlay()) {
			const actor = $gameParty.leader();
			return actor ? actor.stateOverlayIndex() : 0;
		}
		return this._stateOverlayIndex;
	};

	Game_Player.prototype.isAutoStateOverlay = function() {
		return this._stateOverlayIndex === -1;
	};

	//-----------------------------------------------------------------------------
	// Game_Follower

	Game_Follower.prototype.stateOverlayIndex = function() {
		if ($gamePlayer.isAutoStateOverlay()) {
			return this.isVisible() ? this.actor().stateOverlayIndex() : 0;
		}
		return this.isVisible() ? this._stateOverlayIndex : 0;
	};

	//-----------------------------------------------------------------------------
	// Sprite_CharacterOverlay

	function Sprite_CharacterOverlay() {
		this.initialize(...arguments);
	}

	Sprite_CharacterOverlay.prototype = Object.create(Sprite_StateOverlay.prototype);
	Sprite_CharacterOverlay.prototype.constructor = Sprite_CharacterOverlay;

	Sprite_CharacterOverlay.prototype.setup = function(battler) {
		Sprite_StateOverlay.prototype.setup.call(this, battler);
		this._animationCount = this.animationWait();
		this._pattern = 7;
		this.update();
	};

	Sprite_CharacterOverlay.prototype.update = function() {
		Sprite_StateOverlay.prototype.update.call(this);
		this.y = 0;
		if (this.parent) {
			const scale = this.parent.height / this.height * sizeRatio;
			this.scale.x = this.scale.y = Math.max(scale, minScale);
			this.y = (offsetY[this._overlayIndex] || 0) * scale;
		} else {
			this.y = 0;
			this.scale.x = this.scale.y = 1;
		}
	};

	//-----------------------------------------------------------------------------
	// Sprite_Character

	const _Sprite_Character_initMembers = Sprite_Character.prototype.initMembers;
	Sprite_Character.prototype.initMembers = function() {
		_Sprite_Character_initMembers.call(this);
		this._stateOverlayIndex = 0;
		this._stateSprite = null;
	};

	const _Sprite_Character_createHalfBodySprites = Sprite_Character.prototype.createHalfBodySprites;
	Sprite_Character.prototype.createHalfBodySprites = function() {
		const createBody = !this._upperBody;
		_Sprite_Character_createHalfBodySprites.call(this);
		if (createBody && this._stateSprite) {
			this.addChild(this._stateSprite);
		}
	};

	const _Sprite_Character_updateOther = Sprite_Character.prototype.updateOther;
	Sprite_Character.prototype.updateOther = function() {
		_Sprite_Character_updateOther.call(this);
		const index = this._character.stateOverlayIndex() ?? 0;
		if (this._stateOverlayIndex !== index) {
			this._stateOverlayIndex = index;
			if (!this._stateSprite) {
				this._stateSprite = new Sprite_CharacterOverlay();
				this.addChild(this._stateSprite);
			}
			if (index === 0) {
				this._stateSprite.destroy();
				this._stateSprite = null;
			} else {
				this._stateSprite.setup(this._character);
			}
		}
	};

	//-----------------------------------------------------------------------------
	// DataManager

	if (useComments) {
		if (!AWY.addPageSettings) {
			AWY._pageSettingHandlers = [];
			const _DataManager_onLoad = DataManager.onLoad;
			DataManager.onLoad = function(object) {
				_DataManager_onLoad.apply(this, arguments);
				AWY.addPageSettings(object);
			};

			AWY.addPageSettings = function(object) {
				if (DataManager.isMapObject(object) && Array.isArray(object.events)) {
					for (const event of object.events) {
						if (event && event.pages){
							extractMetadata(event);
						}
					}
				}
			};

			function extractMetadata(data) {
				for (const page of data.pages) {
					const comment = findComment(page);
					const commentData = {"note": comment};
					DataManager.extractMetadata(commentData);
					AWY._pageSettingHandlers.forEach(handler => handler(page, commentData.meta));
				}
			}

			function findComment(page) {
				const list = page.list;
				if (!list[0] && list[0].code !== 108) {
					return "";
				}
				let comment = list[0].parameters[0];
				for (let i = 1; list[i] && list[i].code === 408; i++) {
					comment += list[i].parameters[0];
				}
				return comment;
			}
		}

		AWY._pageSettingHandlers.push(
			function(page, meta) {
				page.stateOverlay = meta.stateOverlay || 0;
			}
		);
	}
}