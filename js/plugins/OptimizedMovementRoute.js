// OptimizedMovementRoute.js Ver.1.2.0
// MIT License (C) 2022 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MV MZ
* @plugindesc Optimize movement routes.
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/500608978.html
* @help Ver.1.2.0
* Normally, only one movement route command is processed per frame,
* but this will be changed to allow multiple processing per frame.
*
* [Script]
* this.forceDir(direction); //Forces the direction to change regardless of whether the direction is fixed.
* Down:2 Left:4 Right:6 Up:8
*
* @param dirIsEx
* @text Except for directional commands
* @desc When using directional commands, there is a pause before moving to the next command.
* @type boolean
* @default true
*
* @param forceDir
* @text Force Direction Change
* @desc Standard movement commands always change direction, regardless of whether the direction is fixed.
* @type boolean
* @default false
*
*/

/*:ja
* @target MV MZ
* @plugindesc 移動ルートの設定を最適化します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/500608978.html
* @help 移動ルートのコマンドは通常１フレームに１つしか処理されませんが、
* それを１フレームで複数処理できる仕様に変更します。
*
* [スクリプト]
* this.forceDir(向き); //向きを固定したかに関わらず強制的に向きを変更します。
* 下：2　左：4　右：6　上：8
*
* [更新履歴]
* 2022/02/12：Ver.1.0.0　公開。
* 2023/10/07：Ver.1.0.1　移動ルートの内容が空だった時の挙動を修正。
* 2023/10/14：Ver.1.0.2　前バージョンの不備を修正。
* 2023/12/07：Ver.1.1.0　向きを固定したかに関わらず強制的に向きを変更する機能を追加。
* 2023/12/14：Ver.1.1.1　「プレイヤーに近づく」でプレイヤーと重なっているときにフリーズする問題を解消。
* 2025/01/31：Ver.1.2.0　自律移動の不具合を修正しました。
*
* @param dirIsEx
* @text 向きコマンドは例外とする
* @desc 向きコマンドを使用した場合は次のコマンドに移行するまでに間隔を空けます。
* @type boolean
* @default true
*
* @param forceDir
* @text 強制向き設定
* @desc 向きを固定したかに関わらず標準の移動コマンドでの向き変更を常に行います。
* @type boolean
* @default false
*
*/

'use strict';
{
	const pluginName = document.currentScript.src.match(/^.*\/(.*).js$/)[1];
	const parameters = PluginManager.parameters(pluginName);
	const dirIsEx = parameters["dirIsEx"] === "true";
	const forceDir = parameters["forceDir"] === "true";

	Game_CharacterBase.prototype.forceDir = function(d) {
		const isDirectionFixed = this.isDirectionFixed();
		this.setDirectionFix(false);
		this.setDirection(d);
		this.setDirectionFix(isDirectionFixed);
	};

	let moveTowardCharacter = false;
	const _Game_Character_updateRoutineMove = Game_Character.prototype.updateRoutineMove;
	Game_Character.prototype.updateRoutineMove = function() {
		moveTowardCharacter = false;
		while (1) {
			const lastIndex = this._moveRouteIndex;
			_Game_Character_updateRoutineMove.call(this);
			if (this.shouldBreakHere(lastIndex)) {
				break;
			}
		};
	};

	Game_Character.prototype.shouldBreakHere = function(index) {
		//移動ルートが存在しない or コマンドが存在しない or 長さ1未満
		if (!this._moveRoute || !this._moveRoute.list[index] || this._moveRoute.list.length <= 1) {
			return true;
		}
		//行動失敗
		if (!this.isMovementSucceeded()) {
			return true;
		}
		//ウェイト中
		if (this._waitCount > 0) {
			return true;
		}
		//移動中
		if (!this.isStopping()) {
			return true;
		}
		//キャラクターに近づく
		if (moveTowardCharacter) {
			return true;
		}
		//向き変更
		const command = dirIsEx && this._moveRoute.list[index];
		if (command && command.code >= Game_Character.ROUTE_TURN_DOWN && command.code <= Game_Character.ROUTE_TURN_AWAY) {
			return true;
		}
		return false;
	};

	const _Game_Character_moveTowardCharacter = Game_Character.prototype.moveTowardCharacter;
	Game_Character.prototype.moveTowardCharacter = function(character) {
		moveTowardCharacter = !(this.deltaXFrom(character.x) || this.deltaYFrom(character.y));
		_Game_Character_moveTowardCharacter.call(this, character);
	};

	if (forceDir) {
		const _Game_Character_processMoveCommand = Game_Character.prototype.processMoveCommand;
		Game_Character.prototype.processMoveCommand = function(command) {
			const isDirectionFixed = this.isDirectionFixed();
			const forceDir = isDirectionFixed && command.code <= Game_Character.ROUTE_TURN_AWAY && command.code >= Game_Character.ROUTE_TURN_DOWN;
			if (forceDir) {
				this.setDirectionFix(false);
			}
			_Game_Character_processMoveCommand.call(this, command);
			if (forceDir) {
				this.setDirectionFix(isDirectionFixed);
			}
		};
	}

	const _Game_Character_processMoveCommand = Game_Character.prototype.processMoveCommand;
	Game_Character.prototype.processMoveCommand = function(command) {
		_Game_Character_processMoveCommand.call(this, command);
		if (command.code === Game_Character.ROUTE_WAIT) {
			this._waitCount = command.parameters[0];
		}
	};
}