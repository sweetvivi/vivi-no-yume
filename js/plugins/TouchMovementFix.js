// TouchMovementFix.js Ver.1.0.1
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Fix touch movement.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/510286719.html
* @help Ver.1.0.1
* If the event execution fits into one frame, the touch state will be kept perfectly.
* It also prevents the map destination sprite from appearing in the battle background.
*/

/*:ja
* @target MZ
* @plugindesc タッチ移動を修正します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/510286719.html
* @help イベント実行が1フレームに収まる場合はタッチ状態が完全に保持されます。
* また、マップの行き先のスプライトが戦闘背景に映り込まないようにします。
*
* [更新履歴]
* 2025/02/12：Ver.1.0.0　公開。
* 2025/03/12：Ver.1.0.1　不具合修正。
*/

'use strict';
{
	//-----------------------------------------------------------------------------
	// Game_Player

	const _Game_Player_triggerTouchAction = Game_Player.prototype.triggerTouchAction;
	Game_Player.prototype.triggerTouchAction = function() {
		const triggered = _Game_Player_triggerTouchAction.call(this);
		if (triggered) {
			$gameTemp.clearDestination();
		}
		return triggered;
	};

	//-----------------------------------------------------------------------------
	// Scene_Map

	const _Scene_Map_initialize = Scene_Map.prototype.initialize;
	Scene_Map.prototype.initialize = function() {
		_Scene_Map_initialize.call(this);
		this._destinationStopCount = 0;
		this._keepDestination = false;
	};

	const _Scene_Map_updateDestination = Scene_Map.prototype.updateDestination;
	Scene_Map.prototype.updateDestination = function() {
		this._keepDestination = false;
		if (this.isMapTouchOk()) {
			this._destinationStopCount = 0;
		} else {
			this._destinationStopCount++;
		}
		this._keepDestination = this._destinationStopCount < 2;
		_Scene_Map_updateDestination.call(this);
		this._keepDestination = false;
	};

	const _Scene_Map_isMapTouchOk = Scene_Map.prototype.isMapTouchOk;
	Scene_Map.prototype.isMapTouchOk = function() {
		return _Scene_Map_isMapTouchOk.call(this) || this._keepDestination;
	};

	const _Scene_Map_updateMain = Scene_Map.prototype.updateMain;
	Scene_Map.prototype.updateMain = function() {
		_Scene_Map_updateMain.call(this);
		if (this._destinationStopCount === 1 && !this.isMapTouchOk()) {
			this._destinationStopCount++;
			$gameTemp.clearDestination();
			this._touchCount = 0;
		}
	};

	const _Scene_Map_snapForBattleBackground = Scene_Map.prototype.snapForBattleBackground;
	Scene_Map.prototype.snapForBattleBackground = function() {
		const sprite = this._spriteset && this._spriteset._destinationSprite;
		const v = sprite && sprite.visible;
		if (v) {
			sprite.visible = false;
		}
		_Scene_Map_snapForBattleBackground.call(this);
		if (v) {
			sprite.visible = true;
		}
	};
}