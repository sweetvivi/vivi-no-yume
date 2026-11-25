// WindowAvoidsPlayer.js Ver.3.0.0
// MIT License (C) 2023 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc  Prevents the message window from obscuring the player.
* @orderAfter MessagePlus
* @orderAfter MessageFaceOption
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/499238761.html
* @help Ver.3.0.0
* Functions that reproduce RPG Maker 2000.
* If enabled, the window will be moved to the bottom of the screen
* if the player is at the top of the screen and vice versa.
*
* @param tolerance
* @text Tolerance
* @desc How far from the center of the screen the player needs to be to shift the window position. If auto, the tile width.
* @type combo
* @default auto
*
* @param ignoreMiddle
* @text Ignore Window Position [Middle]
* @desc It does not avoid when the window position is "Middle".
* @type boolean
* @default false
*
* @command enableAvoidance
* @text Enable Avoidance
* @desc If enabled, the window will be moved to the bottom of the screen if the player is at the top and vice versa.
*
* @command disableAvoidance
* @text Disable Avoidance
* @desc Return it to its original state.
*
*/

/*:ja
* @target MZ
* @plugindesc  メッセージウィンドウがプレイヤーに被らないようにします。
* @orderAfter MessagePlus
* @orderAfter MessageFaceOption
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/499238761.html
* @help ツクール2000の再現機能。
* プレイヤーが画面上方に位置している場合はウィンドウを下に、
* 画面下方に位置している場合はウィンドウを上に表示するようにします。
*
* [更新履歴]
* 2023/05/05：Ver.1.0.0　公開。
* 2023/12/18：Ver.1.1.0　不具合修正。
* 2023/12/18：Ver.2.0.0　機能を簡素化。
* 2025/03/01：Ver.3.0.0　リニューアル。前バージョンとの互換性はありません。パラメータ追加。
*
* @param tolerance
* @text 許容値
* @desc プレイヤーが画面中央からどれくらいズレた時にウィンドウの位置を変えるかを数値で指定します。autoならタイル幅に依存。
* @type combo
* @default auto
*
* @param ignoreMiddle
* @text ウィンドウ位置[中]を無視
* @desc ウィンドウ位置が「中」の時は回避しません。
* @type boolean
* @default false
*
* @command enableAvoidance
* @text 回避有効化
* @desc プレイヤーが画面上方に位置している場合はウィンドウを下に、画面下方に位置している場合はウィンドウを上に表示するようにします。
*
* @command disableAvoidance
* @text 回避無効化
* @desc 元に戻します。
*
*/

'use strict';

{
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const parameters = PluginManager.parameters(pluginName);
	const tolerance = Math.abs(parameters["tolerance"]);
	const isAuto = parameters["tolerance"] === "auto";
	const ignoreMiddle = parameters["ignoreMiddle"] === "true";

	//-----------------------------------------------------------------------------
	// PluginManager

	PluginManager.registerCommand(pluginName, "enableAvoidance", _=>$gameSystem.enableWindowPlayerAvoidance());
	PluginManager.registerCommand(pluginName, "disableAvoidance", _=>$gameSystem.disableWindowPlayerAvoidance());

	//-----------------------------------------------------------------------------
	// Game_System

	const _Game_System_initialize = Game_System.prototype.initialize;
	Game_System.prototype.initialize = function() {
		_Game_System_initialize.call(this);
		this._windowPlayerAvoidance = false;
	};

	Game_System.prototype.isWindowPlayerAvoidanceEnabled = function() {
		return this._windowPlayerAvoidance;
	};

	Game_System.prototype.enableWindowPlayerAvoidance = function() {
		this._windowPlayerAvoidance = true;
	};

	Game_System.prototype.disableWindowPlayerAvoidance = function() {
		this._windowPlayerAvoidance = false;
	};

	//-----------------------------------------------------------------------------
	// Game_Message

	const _Game_Message_setPositionType = Game_Message.prototype.setPositionType;
	Game_Message.prototype.setPositionType = function(positionType) {
		const ignore = ignoreMiddle && positionType === 1;
		if (!ignore && $gameSystem.isWindowPlayerAvoidanceEnabled() && SceneManager._scene.constructor === Scene_Map) {
			const gh = Graphics.height / 2;
			const playerY = $gamePlayer.screenY();
			const ty = isAuto ? $gameMap.tileWidth(): tolerance;
			if (Math.abs(gh - playerY) >= ty) {
				positionType = (gh < playerY ? 0 : 2);
			}
		}
		_Game_Message_setPositionType.call(this, positionType);
	};

}