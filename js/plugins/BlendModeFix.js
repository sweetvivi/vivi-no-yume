// BlendModeFix.js Ver.1.0.1
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Improves the issue where the "Change Blend Mode" function did not work properly in filter plug-ins.
* @author あわやまたな (Awayamatana)
* @url https://awaya3ji.seesaa.net/article/510114250.html
* @help Ver.1.0.1
*/

/*:ja
* @target MZ
* @plugindesc フィルター系プラグインで「合成方法の変更」が正常動作しなくなる状況を改善します。
* @author あわやまたな (Awayamatana)
* @url https://awaya3ji.seesaa.net/article/510114250.html
* @help [更新履歴]
* 2025/02/05：Ver.1.0.0　公開。
* 2025/02/14：Ver.1.0.1　挙動修正。
*/

'use strict';

{
	if (Sprite.prototype.updateTransform === PIXI.Sprite.prototype.updateTransform) {
		Sprite.prototype.updateTransform = function() {
			PIXI.Sprite.prototype.updateTransform.apply(this, arguments);
		};
	}

	const _Sprite_updateTransform = Sprite.prototype.updateTransform;
	Sprite.prototype.updateTransform = function() {
		_Sprite_updateTransform.apply(this, arguments);
		if (this.filters) {
			for (const filter of this.filters) {
				filter.blendMode = this._blendMode;
			}
		}
	};
}