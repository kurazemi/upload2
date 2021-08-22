/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
// [START gae_python38_log]
// [START gae_python3_log]
'use strict';
//アップロードを許可する拡張子
var allow_exts = new Array('csv');

function input_check() {
	//ファイルが選択されているかどうかのチェック
	if (file_form.file.value == ""){
		//条件に一致する場合(ファイル名が空の場合)
	    alert("ファイルを選択してください");
	    event.preventDefault();
	    return false;
	}else{
	}

	//拡張子のチェック　比較のため小文字にする
	var ext = getExt(file_form.file.value).toLowerCase();
	//許可する拡張子の一覧(allow_exts)から対象の拡張子があるか確認する
	if (allow_exts.indexOf(ext) === -1){
           alert("ファイルの拡張子を確認してください");    //エラーメッセージを出力
	   event.preventDefault();
	   return false;
	}else{
           return true;
	}
}

//ファイル名から拡張子を取得する関数
function getExt(filename)
{
	var pos = filename.lastIndexOf('.');
	if (pos === -1) return '';
	return filename.slice(pos + 1);
}


//window.addEventListener('load', function () {

//  console.log("Hello World!");

//});
// [END gae_python3_log]
// [END gae_python38_log]
