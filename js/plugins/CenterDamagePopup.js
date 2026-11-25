// CenterDamagePopup.js Ver.1.0.0
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Center the damage popup on the enemy.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/510758164.html
* @help Ver.1.0.0
*
* @param offsetY
* @text Offset Y
* @default 8
*/

/*:ja
* @target MZ
* @plugindesc ダメージポップアップを敵キャラの中央に配置します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/510758164.html
* @help
* [更新履歴]
* 2025/02/25：Ver.1.0.0　公開。
*
* @param offsetY
* @text オフセットY
* @default 8
*/

'use strict';
{
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const parameter = PluginManager.parameters(pluginName);
	const offsetY = Number(parameter.offsetY || 0);

	const _Sprite_Enemy_damageOffsetY = Sprite_Enemy.prototype.damageOffsetY;
	Sprite_Enemy.prototype.damageOffsetY = function() {
		let oy = _Sprite_Enemy_damageOffsetY.call(this);
		const mainSprite = this.mainSprite();
		if (mainSprite) {
			oy -= mainSprite.height * mainSprite.scale.y / 2;
		}
		oy += Sprite_Damage.prototype.fontSize() / 2;
		return oy + offsetY;
	};
}