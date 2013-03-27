/**
 *  Top level JavaScript defining globals and utility functions.
 */


var _ruleCtrl = null;
var _reportCtrl = null;
var _globals = {};
$(document).ready(function() {
	
	// hide the patient selector if in an iframe or load patient details
	if (window != window.top) {
		$('#patient_overview').hide();
		$('#back_to_patient_select').hide();
	}
	else {
		$.ajax({
			'url': 'demographics',
			'dataType': 'json'
		})
		.always(function(obj1, status, obj2) {
			var json = ('success' == status) ? obj1 : (('parsererror' == status) ? {} : null);		// empty JSON generates "parsererror"
			var demo = {};
			if (json) {
				demo = json;
			}
			else {
				console.warn('no good response for demographics', obj1, obj2);
			}
			console.log('demo', demo);
			$('#patient_overview').html('templates/demographics.ejs', {'demo': demo});
		});
	}
	
	_ruleCtrl = new RuleController();
	_ruleCtrl.fetchRules();
})



/**
 *  Sorts medication objects based on their med['sp:drugName']['dcterms:title'] attribute, ascending.
 */
function compareMedByNameASC(a, b) {
	if (!('sp:drugName' in a)) {
		return 1;
	}
	if (!('dcterms:title' in a['sp:drugName'])) {
		return 1;
	}
	if (!('sp:drugName' in b)) {
		return -1;
	}
	if (!('dcterms:title' in b['sp:drugName'])) {
		return -1;
	}
	
	if (a['sp:drugName']['dcterms:title'] < b['sp:drugName']['dcterms:title']) {
		return -1;
	}
	if (a['sp:drugName']['dcterms:title'] > b['sp:drugName']['dcterms:title']) {
		return 1;
	}
	return 0;
}

/**
 *  Sorts objects based on their "date" attribute, descending.
 */
function compareByDateDESC(a, b) {
	if (!('date' in a)) {
		return 1;
	}
	if (!('date' in b)) {
		return -1;
	}
	
	if (parseInt(a.date) < parseInt(b.date)) {
		return 1;
	}
	if (parseInt(a.date) > parseInt(b.date)) {
		return -1;
	}
	return 0;
}

