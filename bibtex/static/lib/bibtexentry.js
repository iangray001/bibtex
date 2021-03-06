/*
Javascript to handle the Bibtex per-field entry method in add.html.

Defines the supported entry types, and the fields that are required/optional.
*/

"use strict";

//title author and year are always shown
var allfields = ['journal', 'publisher', 'booktitle', 'school', 'institution', 'howpublished', 
				'volume', 'number', 'pages', 'month', 'editor', 'series', 'edition']

var bibtexfields_required = {
	article: ['journal'],
	book: ['publisher'],
	inproceedings: ['booktitle'],
	incollection: ['booktitle'],
	misc: [],
	phdthesis: ['school'],
	techreport: ['institution']
}

var bibtexfields_optional = {
	article: ['volume', 'number', 'pages', 'month'],
	book: ['editor', 'volume', 'series', 'edition', 'month'],
	inproceedings: ['editor', 'pages', 'publisher', 'month'],
	incollection: ['editor', 'pages', 'publisher', 'month'],
	misc: ['howpublished', 'month', 'journal', 'publisher', 'booktitle', 'volume', 'number', 'pages', 'month', 'editor', 'series'],
	phdthesis: ['month'],
	techreport: ['number', 'month']
}


var keyChecked = ""

function checkBibtexKey(bib, checkurl, csrf) {
	try {
		var entries = doBibtexParse(bib);

		if("@comments" in entries) {
			delete entries["@comments"];
		}

		if(Object.keys(entries).length == 1) {
			var key = Object.keys(entries)[0];
			keyChecked = key;
			$.ajax({
				type: "POST",
				url: checkurl,
				data: {key: key, csrfmiddlewaretoken: csrf},
				success: checkBibtexKeyReply
			});
		}
	} catch(err) {
		console.log("Error " + err);
	}
}

function checkBibtexKeyReply(data) {
	if(data.startsWith("YES")) {
		$('#keysearchresults').html("<p class='error'>The key " + keyChecked + " already exists in the database. Please select another.</p>");
	} else {
		$('#keysearchresults').html("")
	}
}

function bibtexInputTypeClick(obj) {
	if(obj.name == "entrytype") {
		//Hide all fields
		for(var i = 0; i < allfields.length; i++) {
			$('#tr_' + allfields[i]).hide();
		}

		//Now show the ones we need
		for(var i = 0; i < bibtexfields_required[obj.value].length; i++) {
			$('#tr_' + bibtexfields_required[obj.value][i]).show();
			$('#tr_' + bibtexfields_required[obj.value][i]).addClass('bibtex_required');
			$('#tr_' + bibtexfields_required[obj.value][i]).removeClass('bibtex_optional');
		}
		for(var i = 0; i < bibtexfields_optional[obj.value].length; i++) {
			$('#tr_' + bibtexfields_optional[obj.value][i]).show();
			$('#tr_' + bibtexfields_optional[obj.value][i]).addClass('bibtex_optional');
			$('#tr_' + bibtexfields_optional[obj.value][i]).removeClass('bibtex_required');
		}
	}
}