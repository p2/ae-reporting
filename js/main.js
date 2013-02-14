/**
 *  One file to rule them all.
 */


var _ruleCtrl = null;
var _globals = {};
$(document).ready(function() {
	_ruleCtrl = new RuleController();
	_ruleCtrl.fetchRules();
})


/**
 *  The rule model.
 */
var Rule = Base.extend({
	name: '',
	description: '',
	
	constructor: function(json) {
		this.id = ('id' in json) ? json.id : '';
		this.name = ('name' in json) ? json.name : '';
		this.description = ('description' in json) ? json.description : '';
	},
	
	run: function(sender) {
		var self = this;
		var btn = $(sender);
		btn.text("Running...").attr('disabled', true);
		
		$.ajax('rules/' + self.id + '/run_against/' + _record_id + '?api_base=' + _api_base, {
			success: function(response) {
				var area = btn.parent().find('.rule_output').first();
				btn.text("Check").removeAttr('disabled');
				
				// no match
				if (0 == response) {
					if (area.is("*")) {
						area.empty().html("<i>No match</i>");
					}
					else {
						alert("The rule did not match");
					}
				}
				
				// match
				else {
					if (area.is("*")) {
						area.empty().append("<h3>The rule did match</h3>").append('<pre/>');
						area.find('pre').first().text(response);
					}
					else {
						alert("The rule did match");
					}
				}
			},
			error: function(jqXHR, textStatus, errorThrown ) {
				alert('Failed to run rule ' + self.name + ': ' + errorThrown);
				btn.text("Try again").removeAttr('disabled');
			}
		});
	}
});


/**
 *	The rule controller.
 */
var RuleController = Base.extend({
	loaded: false,
	rules: [],
	
	fetchRules: function() {
		var self = this;
		$.get('rules/', function(json) {
			if (json) {
				var rls = [];
				for (var i = 0; i < json.length; i++) {
					rls.push(new Rule(json[i]));
				};
				self.rules = rls;
				self.loaded = true;
				
				self.showRules();
			}
			else {
				alert('Invalid response for "rules/"');
				console.log('rules', json);
			}
		}, 'json');
	},
	
	showRules: function() {
		$('#rules').html('templates/rules.ejs', {rules: this.rules});
	}
});


// let's hack
function _call(func) {
	if (func && 'function' == typeof func) {
		if (undefined === func.id) {
			func.id = Math.round((new Date()).getTime() * 1000) + '' + Math.round(Math.random() * 1000);
		}
		_globals[func.id] = func;
		return "_doCall(this, '" + func.id + "')";
	}
	return '';
}

function _doCall(sender, call_id) {
	var func = _globals[call_id];
	if (func) {
		func(sender);
	}
	else {
		console.error('No call for id', call_id);
	}
}

