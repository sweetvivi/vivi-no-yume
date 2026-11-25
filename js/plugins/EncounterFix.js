// EncounterFix.js Ver.1.0.0
// MIT License (C) 2024 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc Prevents unnecessary effects from appearing in the encounter effect and the battle background.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/505477386.html
* @help Ver.1.0.0
*
* @param hideEffects
* @text Hide Effects
* @desc Balloons and animations are not displayed in the encounter effect.
* @type boolean
* @default true
*
* @param hidePictures
* @text Hide Pictures
* @desc No pictures are displayed in the battle background.
* It is effective when the battle background is (None).
* @type boolean
* @default false
*
* @param dsStyle
* @text DS Style (Bonus)
* @desc Makes the battle background look like RPG Maker DS.
* It is effective when the battle background is (None).
* @type boolean
* @default false
*
*/

/*:ja
* @target MZ
* @plugindesc エンカウントエフェクトや戦闘背景に余計なエフェクトが映り込むことを防ぎます。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/505477386.html
* @help
* [更新履歴]
* 2024/10/31：Ver.1.0.0　公開。
*
* @param hideEffects
* @text エフェクトを隠す
* @desc エンカウントエフェクト中にフキダシやアニメーションを表示しません。
* @type boolean
* @default true
*
* @param hidePictures
* @text ピクチャを隠す
* @desc 戦闘背景にピクチャを表示しません。
* 戦闘背景が（なし）のときに効果を発揮します。
* @type boolean
* @default false
*
* @param dsStyle
* @text DS風（おまけ）
* @desc 戦闘背景をツクールDSのようにします。
* 戦闘背景が（なし）のときに効果を発揮します。
* @type boolean
* @default false
*
*/
'use strict';
{
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const params = PluginManager.parameters(pluginName);

	const _Scene_Map_startEncounterEffect = Scene_Map.prototype.startEncounterEffect;
	Scene_Map.prototype.startEncounterEffect = function() {
		if (params.hideEffects === "true") {
			const effects = this._spriteset._balloonSprites.concat(this._spriteset._animationSprites);
			effects.forEach(s=>s.hide());
			while ($gameTemp.retrieveAnimation()) {}
			while ($gameTemp.retrieveBalloon()) {}
		}
		_Scene_Map_startEncounterEffect.call(this);
	};

	const _Scene_Map_snapForBattleBackground = Scene_Map.prototype.snapForBattleBackground;
	Scene_Map.prototype.snapForBattleBackground = function() {
		const pics = this._spriteset._pictureContainer;
		const visible = pics.visible;
		if (params.hidePictures === "true") pics.visible = false;
		_Scene_Map_snapForBattleBackground.call(this);
		pics.visible = visible;
	};

	if (params.dsStyle === "true") {
		const _Scene_Map_snapForBattleBackground = Scene_Map.prototype.snapForBattleBackground;
		Scene_Map.prototype.snapForBattleBackground = function() {
			const characters = [$gamePlayer].concat($gamePlayer.followers().data());
			const sprites = characters.map(c => this._spriteset.findTargetSprite(c)).filter(s => s && s.visible);
			sprites.forEach(s => s.visible = false);
			_Scene_Map_snapForBattleBackground.call(this);
			sprites.forEach(s => s.visible = true);
		};

		Spriteset_Map.prototype.hideCharacters = function() {};

		const _Spriteset_Battle_createBackground = Spriteset_Battle.prototype.createBackground;
		Spriteset_Battle.prototype.createBackground = function() {
			_Spriteset_Battle_createBackground.call(this);
			const filters = this._backgroundSprite.filters;
			if (filters) {
				filters.forEach(f=>f.enabled = false);
			}
			this._backgroundSprite.opacity = 192;
		};
	}
}