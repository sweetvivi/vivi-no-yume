// SceneStartFix.js Ver.1.0.0
// MIT License (C) 2024 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Prevents flickering of the character immediately after the map is displayed.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/505462688.html
* @help Ver.1.0.0
*
*/

/*:ja
* @target MZ
* @plugindesc マップ表示直後のキャラクターのちらつきを防ぎます。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/505462688.html
* @help 
* [更新履歴]
* 2024/10/30：Ver.1.0.0　公開。
*
*/
'use strict';
{
	const _SceneManager_onSceneStart = SceneManager.onSceneStart;
	SceneManager.onSceneStart = function() {
		_SceneManager_onSceneStart.call(this);
		this._scene.update();
	};
}