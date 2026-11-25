// SmoothFont.js Ver.1.0.0
// MIT License (C) 2024 あわやまたな
// http://opensource.org/licenses/mit-license.php

/*:
* @target MV MZ
* @plugindesc Smooths fonts.
* @author あわやまたな (Awayamatana)
* @url https://awaya3ji.seesaa.net/article/503140532.html
* @help Ver.1.0.0
* Prevents characters from appearing jagged when the font size is less than 21 pixels.
*
*/

/*:ja
* @target MV MZ
* @plugindesc フォントを滑らかにします。
* @author あわやまたな (Awayamatana)
* @url https://awaya3ji.seesaa.net/article/503140532.html
* @help フォントサイズが21px未満になると文字がガタガタになる現象を回避します。
*
* [更新履歴]
* 2024/04/27：Ver.1.0.0　公開。
*
*/

'use strict';

{

	//-----------------------------------------------------------------------------
	// Bitmap

	// フォントを0.03度傾けて描画して回避する。
	const _Bitmap_drawText = Bitmap.prototype.drawText;
	Bitmap.prototype.drawText = function(text, x, y, maxWidth, lineHeight, align) {
		const context = this.context;
		context.save();
		if (this.fontSize < 21) {
			context.rotate(0.03 * Math.PI / 180);
		}
		_Bitmap_drawText.apply(this, arguments);
		context.restore();
	};

}