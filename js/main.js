/**
 *  One file to rule them all.
 */


var _ruleCtrl = null;
var _globals = {};
$(document).ready(function() {
	
	// hide the patient selector if in an iframe
	if (window != window.top) {
		$('#back_to_patient_select').hide();
	}
	
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
		for (var p in json) {
			this[p] = json[p];
		}
	},
	
	hasPendingResults: function() {
		console.log(this.last_results);
		if (this.last_results && this.last_results.length > 0) {
			for (var i = 0; i < this.last_results.length; i++) {
				if (this.last_results[i].flag) {
					return true;
				}
			};
		}
		return false;
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
				if ('ok' == response) {
					if (area.is("*")) {
						area.empty().html('<h3 class="green">No match</h3>');
					}
					else {
						alert("The rule did not match");
					}
				}
				
				// match
				else {
					if (area.is("*")) {
						area.empty().append('<h3 class="red">The rule did match</h3>').append('<pre/>');
						area.find('pre').first().text(response);
					}
					else {
						alert("The rule did match");
					}
				}
				
				// update UI
				var prev = $('#num_previous_checks_' + self.id);
				prev.text(prev.text() *1 + 1);
			},
			error: function(jqXHR, textStatus, errorThrown ) {
				var area = btn.parent().find('.rule_output').first();
				btn.text("Try again").removeAttr('disabled');
				
				if (area.is("*")) {
					area.empty().html('<h3 class="red">Failed to run rule ' + self.name + ': ' + errorThrown + '</h3>');
				}
				else {
					alert('Failed to run rule ' + self.name + ': ' + errorThrown);
				}
			}
		});
	},
	
	report: function(sender) {
		var self = this;
		btn.text("Running...").attr('disabled', true);
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
		$.get('rules/?api_base=' + _api_base + '&record_id=' + _record_id, function(json) {
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
	
	// lists all rules by sorting out rules with pending reports first and listing them atop
	showRules: function() {
		var inbox = [];
		var rules = [];
		
		for (var i = 0; i < this.rules.length; i++) {
			var rule = this.rules[i];
			if (rule.hasPendingResults()) {
				inbox.push(rule);
			}
			else {
				rules.push(rule);
			}
		};
		$('#rules').html('templates/rules.ejs', {inbox: inbox, rules: rules});
	},
	
	runRule: function(sender, rule_name) {
		var rule = this._getRule(rule_name);
		if (!rule) {
			alert("We don't have the rule \"" + rule_name + "\"");
			return;
		}
		
		rule.run(sender);
	},
	
	reportRule: function(sender, rule_name) {
		var rule = this._getRule(rule_name);
		if (!rule) {
			alert("We don't have the rule \"" + rule_name + "\"");
			return;
		}
		
		rule.report(sender);
	},
	
	_getRule: function(rule_name) {
		for (var i = 0; i < this.rules.length; i++) {
			if (rule_name == this.rules[i].id) {
				return this.rules[i];
			}
		};
		return null;
	}
});


/**
 *  Runs the rule with the given name.
 */
function _runRule(sender, rule_name) {
	if (!_ruleCtrl) {
		alert("There is no rule controller, cannot run rule!");
		return;
	}
	_ruleCtrl.runRule(sender, rule_name);
}

/**
 *  Initiates the reporting process for the rule with the given name.
 */
function _reportRule(sender, rule_name) {
	if (!_ruleCtrl) {
		alert("There is no rule controller, cannot run rule!");
		return;
	}
	_ruleCtrl.reportRule(sender, rule_name);
}

