// OptimizedScrollingText.js Ver.1.0.0
// MIT License (C) 2025 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MZ
* @plugindesc 文章のスクロールの処理落ちを軽減します。
* @author あわやまたな (Awaya_Matana)
* @url https://awaya3ji.seesaa.net/article/518170080.html
* @help 全ての描画を最初に行うことでスクロール中のカクつきを無くします。
*
* [更新履歴]
* 2025/09/17：Ver.1.0.0　公開。
*
*/

'use strict';

{
	//-----------------------------------------------------------------------------
	// Window_ScrollText

	const _Window_ScrollText_initialize = Window_ScrollText.prototype.initialize;
	Window_ScrollText.prototype.initialize = function(rect) {
		this._textSprites = [];
		_Window_ScrollText_initialize.apply(this, arguments);
	};

	if (Window_ScrollText.prototype.destroy === Window_Base.prototype.destroy) {
		Window_ScrollText.prototype.destroy = function(options) {
			Window_Base.prototype.destroy.apply(this, arguments);
		};
	}

	const _Window_ScrollText_destroy = Window_ScrollText.prototype.destroy;
	Window_ScrollText.prototype.destroy = function(options) {
		_Window_ScrollText_destroy.apply(this, arguments);
		this.destroyTextSprites();
	};

	Window_ScrollText.prototype.destroyTextSprites = function() {
		for (const sprite of this._textSprites.clone()) {
			this._textSprites.remove(sprite);
			sprite.bitmap.destroy();
			sprite.destroy();
		}
	};

	let startMessage = false;
	const _Window_ScrollText_startMessage = Window_ScrollText.prototype.startMessage;
	Window_ScrollText.prototype.startMessage = function() {
		startMessage = true;
		this.destroyTextSprites();
		_Window_ScrollText_startMessage.call(this);
		startMessage = false;
	};

	const _Window_ScrollText_refresh = Window_ScrollText.prototype.refresh;
	Window_ScrollText.prototype.refresh = function() {
		if (startMessage) {
			_Window_ScrollText_refresh.call(this);
			const maxIndex = Math.floor(this._allTextHeight / this._blockHeight);
			if (maxIndex > 0) {
				for (let i = 0; i <= maxIndex; i++) {
					const sprite = new Sprite(new Bitmap(this.contentsWidth(), this._maxBitmapHeight));
					this._textSprites.push(sprite);
					this._clientArea.addChild(sprite);
					sprite.bitmap.blt(this.contents, 0, i * this._blockHeight, sprite.width, sprite.height, 0, 0);
				}
				this.contents.destroy();
				this.contentsBack.destroy();
				this._contentsSprite.bitmap = new Bitmap(1, 1);
				this._contentsBackSprite.bitmap = new Bitmap(1, 1);
			}
		}
		if (this._textSprites.length > 0) {
			this._textSprites.forEach(sprite => sprite.hide());
			this._textSprites[this._blockIndex].show();
		}
	};

	Window_ScrollText.prototype.contentsHeight = function() {
		return Math.max(this._allTextHeight, 1);
	};

	const _Window_ScrollText_terminateMessage = Window_ScrollText.prototype.terminateMessage;
	Window_ScrollText.prototype.terminateMessage = function() {
		_Window_ScrollText_terminateMessage.call(this);
		this.destroyTextSprites();
	};
}