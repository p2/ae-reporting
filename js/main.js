/**
 *  One file to rule them all.
 */


var _ruleCtrl = null;
var _reportCtrl = null;
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
		
		$.ajax('rules/' + self.id + '/run', {
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
		if (_reportCtrl) {
			// do something
		}
		
		_reportCtrl = new ProcessController(this);
		_reportCtrl.init(['demographics', 'adverse_event', 'medications', 'reporter']);
		
		// TODO: this should probably go to another controller
		$('#rules').hide();
		$('#processing').show();
	},
	
	reportDidAbort: function() {
		// TODO: this seems also wrong here
		$('#rules').show();
		$('#processing').hide();
		
		_reportCtrl = null;
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


/**
 *  Controls the processing flow.
 */
var ProcessController = Base.extend({
	for_rule: null,
	sections: [],
	first: null,
	data: null,
	all: ['demographics', 'adverse_event', 'medications', 'labs', 'reporter'],
	names: ["Demographics & Vitals", "Adverse Event", "Medications", "Labs", "Reporter"],
	elem: null,
	
	constructor: function(rule) {
		this.for_rule = rule;
	},
	
	init: function(sections) {
		if (!sections || sections.length < 1) {
			alert("No sections to process, giving up");
			return;
		}
		
		this.elem = $('#processing');
		this.elem.empty();
		this.sections = sections;
		
		// abort header
		var but = $('<button/>').text('Abort');
		var self = this;
		but.click(function() { self.abort(); });
		this.elem.append(but);
		
		// rule info
		var info = $('<div/>').addClass('rule_info');
		info.append('<h3>' + this.for_rule.name + '</h3>');
		info.append('<p>' + this.for_rule.description + '</p>');
		this.elem.append(info);
		
		// setup our sections
		this.first = null;
		for (var i = 0; i < this.all.length; i++) {
			if ($.inArray(this.all[i], sections) >= 0) {
				this._initSection(this.all[i], this.names[i], !this.first);
				if (!this.first) {
					this.first = this.all[i];
				}
			}
		}
		
		// load data
		this._loadData();
	},
	
	_initSection: function(section_id, section_name, do_start) {
		if (!section_id || !this.elem) {
			console.error('_initSection(), section_id', section_id, 'elem', this.elem);
			return;
		}
		var self = this;
		
		// header
		var div = $('<div/>').attr('id', 'proc_' + section_id);
		var head = $('<div/>').addClass('proc_header');
		var section_title = $('<h4/>').text(section_name ? section_name : "Unknown Section");
		head.click({ section_id: section_id }, _toggleSection);
		head.append(section_title);
		div.append(head);
		this.elem.append(div);
		
		// add the body
		var body = $('<div/>').addClass('proc_body');
		body.html("<p>Loading...</p>");
		div.append(body);
		if (do_start) {
			div.addClass('active');
		}
	},
	
	/**
	 *  Retrieves the data that is necessary to prefill the given section.
	 */
	_loadData: function() {
		var self = this;
		var sections = this.sections.join('+');
		$.ajax({
			'url': 'prefill_rule/' + self.for_rule.name + '/' + sections,
			'dataType': 'json'
		})
		.always(function(obj1, status, obj2) {
			var json = ('success' == status) ? obj1 : (('parsererror' == status) ? {} : null);		// empty JSON generates "parsererror"
			if (json) {
				self.data = json;
			}
			else {
				console.warn('no good response for sections', sections, obj1, obj2);
			}
			self._startSection(null, self.first);
		});
	},
	
	_startSection: function(sender, section_id) {
		if (!section_id || !this.elem) {
			console.error('_startSection(), section_id', section_id, 'elem', this.elem);
			return;
		}
		
		// show the section
		var parent = $('#proc_' + section_id);
		parent.addClass('active');
		var div = parent.find('.proc_body').first();
		div.html('templates/process_' + section_id + '.ejs', {'data': this.data});
		
		// add proceed button
		var cont = $('<button/>').text('Proceed').click({ 'section_id': section_id }, _processNextSection);
		var cont_parent = $('<p/>').addClass('process_next');
		cont_parent.append(cont);
		div.append(cont_parent);
		
		// load date pickers (must do manually, the auto-trigger doesn't work for EJS)
		div.find('.auto-kal').each(function(i, elem) {
			$(elem).kalendae({'format': 'MM/DD/YYYY'});
		});
	},
	
	/**
	 *  Starts the next section.
	 */
	startNextSection: function(sender, current_id) {
		var next = null;
		for (var i = 0; i < this.sections.length; i++) {
			if (current_id == this.sections[i]) {
				
				// got a next section
				if (this.sections.length > i+1) {
					next = this.sections[i+1];
				}
				
				// at the end
				else {
					this.finish();
				}
				break;
			}
		}
		
		if (next) {
			this._hideSection(sender, current_id);
			this._startSection(sender, next);
		}
	},
	
	toggleSection: function(sender, section_id) {
		var div = $('#proc_' + section_id);
		if (div.hasClass('active')) {
			this._hideSection(sender, section_id);
		}
		else {
			this._startSection(sender, section_id);
		}
	},
	
	_hideSection: function(sender, section_id) {
		$('#proc_' + section_id).removeClass('active');
	},
	
	/**
	 *  Finish the reporting.
	 */
	finish: function(sender) {
		alert("I don't know how to finish yet");
	},
	
	/**
	 *  Abort the reporting process.
	 */
	abort: function(sender) {
		this.for_rule.reportDidAbort();
	},
	
	
	/**
	 *  Utilities
	 */
});


/**
 *  Starts section.
 */
 function _toggleSection(event) {
 	if (!_reportCtrl) {
 		alert("There is no process controller in place, cannot proceed");
 		return;
 	}
 	
 	_reportCtrl.toggleSection($(event.target), event.data.section_id);
 }
 
 /**
 *  Jumps to next section.
 */
 function _processNextSection(event) {
 	if (!_reportCtrl) {
 		alert("There is no process controller in place, cannot proceed");
 		return;
 	}
 	
 	_reportCtrl.startNextSection($(event.target), event.data.section_id);
 }

