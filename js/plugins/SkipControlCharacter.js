// SkipControlCharacter.js Ver.1.0.0
// MIT License (C) 2024 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Eliminates display delays caused by control characters.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/485154167.html
* @help Ver.1.0.0
* This skips the wait that occurs one frame for each control character.
*
* @param ExclusionList
* @text Exclusion List
* @desc Control characters in the exclude list do not skip the wait.
* It also recognizes lowercase letters.
* @default ["I","<"]
* @type string[]
*
*/

/*:ja
* @target MZ
* @plugindesc 制御文字による表示遅延を解消します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/485154167.html
* @help 制御文字ひとつにつき１フレーム発生するウェイトをスキップします。
* [更新履歴]
* 2022/01/10：Ver.1.0.0　公開。
*
* @param ExclusionList
* @text 除外リスト
* @desc 除外リストに含まれる制御文字はウェイトをスキップしません。
* 小文字でも可。
* @default ["I","<"]
* @type string[]
*
*/
'use strict';
{
	const pluginName = document.currentScript.src.replace(/^.*\/(.*).js$/, (_, p) => p);
	const parameter = PluginManager.parameters(pluginName);
	const exclusionList = new Set(JSON.parse(parameter['ExclusionList']).map(s => s.toUpperCase()));
	let skipControlCharacter;

	const _Window_Base_processCharacter = Window_Base.prototype.processCharacter;
	Window_Base.prototype.processCharacter = function(textState, c) {
		skipControlCharacter = false;
		_Window_Base_processCharacter.apply(this, arguments);
	};

	const _Window_Message_processControlCharacter = Window_Message.prototype.processControlCharacter;
	Window_Message.prototype.processControlCharacter = function(textState, c) {
		skipControlCharacter = true;
		_Window_Message_processControlCharacter.apply(this, arguments);
	};

	const _Window_Message_processEscapeCharacter = Window_Message.prototype.processEscapeCharacter;
	Window_Message.prototype.processEscapeCharacter = function(code, textState) {
		skipControlCharacter = !exclusionList.has(code);
		_Window_Message_processEscapeCharacter.apply(this, arguments);
	};

	Window_Message.prototype.shouldBreakHere = function(textState) {
		if (this.canBreakHere(textState)) {
			if (!this._showFast && !this._lineShowFast && !skipControlCharacter) {
				return true;
			}
			// MZ 用 pause / _waitCount，MV 才有 isWaiting()
			const waiting = this.isWaiting ? this.isWaiting() : (this.pause || this._waitCount > 0);
			if (waiting) {
				return true;
			}
		}
		return false;
	};
}