// EquipStatusFix.js Ver.1.0.0
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @orderAfter LayoutForWvga
* @plugindesc 装備画面に最大HP、最大MPを表示します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/517805672.html
* @help [更新履歴]
* 2025/08/28：Ver.1.0.0　公開。
*
* @param showCharacter
* @text キャラクター表示
* @default true
* @type boolean
*
* @param showFace
* @text 顔表示
* @desc 標準解像度だとはみ出ます。
* @default false
* @type boolean
*
*/

'use strict';
{

	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const params = PluginManager.parameters(pluginName);
	const showCharacter = params.showCharacter === "true";
	const showFace = params.showFace === "true";

	Window_EquipStatus.prototype.refresh = function() {
		this.contents.clear();
		if (this._actor) {
			const nameRect = this.itemLineRect(0);
			if (showCharacter) this.drawActorCharacter(this._actor, nameRect.x + Math.floor(nameRect.width*0.9)-2, this.lineHeight()*2-2);
			if (showFace) this.drawActorFace(this._actor, nameRect.x, nameRect.height);
			this.drawActorName(this._actor, nameRect.x, 0, nameRect.width);
			this.drawAllParams();
		}
	};

	Window_EquipStatus.prototype.drawAllParams = function() {
		for (let i = 0; i < 8; i++) {
			const x = this.itemPadding();
			const y = this.paramY(i);
			this.drawItem(x, y, i);
		}
	};

	if (!showFace) {
		Window_EquipStatus.prototype.paramY = function(index) {
			return Math.floor(this.lineHeight() * (index + 2));
		};
	}
}