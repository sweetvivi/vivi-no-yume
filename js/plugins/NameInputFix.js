// NameInputFix.js Ver.1.0.0
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Fix Name Input Processing.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/516033500.html
* @help Ver.1.0.0
* Fixes a bug that causes the game to be forced to terminate.
* Also, if the player tries to erase the zeroth character, a buzzer will sound.
*/

/*:ja
* @target MZ
* @plugindesc 名前入力の処理を修正します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/516033500.html
* @help ゲームが強制終了してしまう不具合を修正します。
* また、0文字目の時に消去しようとするとブザーを鳴らすようにします。
*
* [更新履歴]
* 2025/06/08：Ver.1.0.0　公開。
*/

'use strict';
{
	//-----------------------------------------------------------------------------
	// Window_NameInput

	Window_NameInput.prototype.processBack = function() {
		if (this._editWindow.back()) {
			SoundManager.playCancel();
		} else {
			SoundManager.playBuzzer();
		}
	};

	//-----------------------------------------------------------------------------
	// Scene_Name

	const _Scene_Name_onInputOk = Scene_Name.prototype.onInputOk;
	Scene_Name.prototype.onInputOk = function() {
		_Scene_Name_onInputOk.call(this);
		this._inputWindow.deactivate();
	};
}