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
	
	allChecksNegative: function() {
		if (this.last_results && this.last_results.length > 0) {
			for (var i = 0; i < this.last_results.length; i++) {
				if (this.last_results[i].flag) {
					return false;
				}
			};
			return true;
		}
		return false;
	},
	
	latestResult: function() {
		var results = [];
		if (this.last_results && this.last_results.length > 0) {
			for (var i = 0; i < this.last_results.length; i++) {
				results.push(this.last_results[i]);
			};
		}
		
		// do we have positive hits at all?
		if (results.length < 1) {
			return null;
		}
		
		// yes, return the latest
		results.sort(compareByDateDESC);
		return results[0];
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
	
	latestPendingResult: function() {
		var hit_results = [];
		if (this.last_results && this.last_results.length > 0) {
			for (var i = 0; i < this.last_results.length; i++) {
				if (this.last_results[i].flag) {
					hit_results.push(this.last_results[i]);
				}
			};
		}
		
		// do we have positive hits at all?
		if (hit_results.length < 1) {
			return null;
		}
		
		// yes, return the latest
		hit_results.sort(compareByDateDESC);
		return hit_results[0];
	},
	
	run: function(sender) {
		var self = this;
		var btn = $(sender);
		btn.text("Running...").attr('disabled', true);
		
		$.ajax('rules/' + self.id + '/run', {
			success: function(response) {
				btn.text("Check").removeAttr('disabled');
				var div = btn.parentsUntil('.rule').parent();
				
				// no match
				if ('ok' == response) {
					div.addClass('all_good');
					if ('rule_box' != div.parent().attr('id')) {
						$('#rule_box').append(div);
					}
				}
				
				// match
				else {
					div.removeClass('all_good');
					if ('rule_inbox' != div.parent().attr('id')) {
						$('#rule_inbox').show().append(div);
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
			console.warn("report controller is already present");
		}
		
		_reportCtrl = new ProcessController(this);
		_reportCtrl.init(['demographics', 'adverse_event', 'problems', 'medications', 'reporter']);
		
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
