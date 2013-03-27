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
		
		// rule info
		var info = $('<div/>').addClass('rule_info');
		info.append('<h3>Reporting: ' + this.for_rule.name + '</h3>');
		info.append('<p>' + this.for_rule.description + '</p>');
		info.append(but);
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
		head.click({ section_id: section_id }, toggleSection);
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
			'url': 'prefill/' + sections,
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
		div.html('templates/process_' + section_id + '.ejs', {'data': this.data, 'rule': this.for_rule});
		
		// add proceed button
		var cont = $('<button/>').text('Proceed').click({ 'section_id': section_id }, processNextSection);
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
function toggleSection(event) {
 	if (!_reportCtrl) {
 		alert("There is no process controller in place, cannot proceed");
 		return;
 	}
 	
 	_reportCtrl.toggleSection($(event.target), event.data.section_id);
}
 
 /**
 *  Jumps to next section.
 */
function processNextSection(event) {
 	if (!_reportCtrl) {
 		alert("There is no process controller in place, cannot proceed");
 		return;
 	}
 	
 	_reportCtrl.startNextSection($(event.target), event.data.section_id);
}
 
/**
 *  Add another empty checkable list item.
 */
function addCheckableListItem(li_item, item_name) {
	if (!li_item || !item_name) {
		console.log("addCheckableListItem(): I need a list item and an item name");
		return;
	}
	
	var html_id = item_name + (new Date().getTime());
	var html = '<input type="checkbox" name="' + item_name + '" value="" checked="checked" />';
	html += '<input type="text" id="' + html_id + '" name="' + html_id + '" />';
	html += '<a href="javascript:void(0);" class="small" onclick="$(this).parent().fadeOut(\'fast\', function(){$(this).remove();})">Remove</a>';
	html += '<br />';
	html += '<input type="text" class="small" id="supplement_' + html_id + '" name="supplement_' + html_id + '" placeholder="date range" style="margin-left:1.2em;" />';
	
	var li = $('<li/>').addClass('additional_item').html(html);
	$(li_item).before(li);
	
	$('#' + html_id).focus();
}

/**
 *  Shows the death date hint IF it is not set.
 */
function showHideDeathHint(show) {
	if (show && !$('#death_date').val()) {
		$('#death_date_hint').show();
	}
	else {
		$('#death_date_hint').hide();
	}
}
