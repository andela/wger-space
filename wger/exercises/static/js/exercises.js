/*
 This file is part of wger Workout Manager.

 wger Workout Manager is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 wger Workout Manager is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 */

/*
 wger exercise functions
 */

'use strict';

/*
 Highlight a muscle in the overview
 */
function wgerHighlightMuscle(element) {
  var $muscle;
  var muscleId;
  var isFront;
  var divId;
  divId = $(element).data('target');
  isFront = ($(element).data('isFront') === 'True') ? 'front' : 'back';
  muscleId = divId.match(/\d+/);

  // Reset all other highlighted muscles
  $muscle = $('.muscle');
  $muscle.removeClass('muscle-active');
  $muscle.addClass('muscle-inactive');

  // Highlight the current one
  $(element).removeClass('muscle-inactive');
  $(element).addClass('muscle-active');

  // Set the corresponding background
  $('#muscle-system').css('background-image',
    'url(/static/images/muscles/main/muscle-' + muscleId + '.svg),' +
    'url(/static/images/muscles/muscular_system_' + isFront + '.svg)');

  // Show the corresponding exercises
  $('.exercise-list').hide();
  $('#' + divId).show();
}


function no_highlight(e){
  var $muscle;
  $muscle = $('.muscle');
  $muscle.removeClass('muscle-active'); 
  $muscle.addClass('muscle-inactive');
  $(e).removeClass('muscle-inactive');
  $(e).addClass('muscle-active').css('background', 'none');
};

function operations(muscleId,url,hide,e){
  $('.muscle-background').css('background-image',
    'url(/static/images/muscles/main/muscle-'+ muscleId +'.svg),' + url);
  no_highlight(e)
  hide
  $('#muscle-'+ muscleId).show();
};

$(document).ready(function(){
  $('.muscle-background').mousemove(function(e){
      var m = e.offsetX;
      var n = e.offsetY;
      var front_url = 'url(/static/images/muscles/muscular_system_front.svg)'
      var hide = $('.exercise-list').hide();
      var back_url = 'url(/static/images/muscles/muscular_system_back.svg)'
      var a, b ,b1, c, d, e1, e2, f,f1, g, g1, h, h1, t;

      a = ( m <= 103 && m >= 49) && (n >= 51 && n <= 72 )
      b= ( m <= 111 && m >= 102) && (n >= 73 && n <= 94 ) 
      b1 = ( m <=46 && m >= 35) && (n >= 72 && n <= 97 )
      c = (m <= 101 && m >= 50) && (n >= 144 && n <= 186 )
      d = ( m <= 85 && m >=64) && (n >= 89 && n <= 135 )
      e1 = ( m <= 110 && m >= 104) && (n >= 50 && n <= 64 ) 
      e2= ( m <=48 && m >= 36) && (n >= 50 && n <= 64 )
      f = ( m <= 100 && m >= 92) && (n >= 77 && n <= 100 )
      f1 = ( m <=60 && m >= 48) && (n >= 78 && n <= 107 )
      g = ( m <= 98 && m >= 87) && (n >= 90 && n <= 129 )
      g1 = ( m <=63 && m >= 52) && (n >= 108 && n <= 126 )
      h = ( m <= 98 && m >= 79) && (n >= 204 && n <= 262 ) 
      h1= ( m <=73 && m >= 52) && (n >= 204 && n <= 262 )
      t = ( m <= 98 && m >=54) && (n >= 32 && n <= 49 )

      if (a){operations(4,front_url,hide,e)}
      else if(b || b1){operations(1, front_url, hide, e)}
      else if(c){operations(10,front_url, hide, e)}
      else if(d){operations(6, front_url, hide, e)}
      else if(e1 || e2){operations(2, front_url,hide,e)}
      else if(f || f1){operations(3, front_url, hide, e)}
      else if(g || g1){operations(14, front_url, hide, e)}
      else if(h || h1){operations(7, back_url, hide, e)}
      else if(t){operations(9, back_url, hide, e)};});
});

/*
 D3js functions
 */

function wgerDrawWeightLogChart(data, divId) {
  var chartData;
  var legend;
  var minValues;
  var i;
  if (data.length) {
    legend = [];
    minValues = [];
    chartData = [];
    for (i = 0; i < data.length; i++) {
      chartData[i] = MG.convert.date(data[i], 'date');

      // Read the possible repetitions for the chart legend
      legend[i] = data[i][0].reps;

      // Read the minimum values for each repetition
      minValues[i] = d3.min(data[i], function (repetitionData) {
        return repetitionData.weight;
      });
    }

    MG.data_graphic({
      data: chartData,
      y_accessor: 'weight',
      min_y: d3.min(minValues),
      aggregate_rollover: true,
      full_width: true,
      top: 10,
      left: 30,
      right: 10,
      height: 200,
      legend: legend,
      target: '#svg-' + divId,
      colors: ['#204a87', '#4e9a06', '#ce5c00', '#5c3566', '#2e3436', '8f5902', '#a40000']
    });
  }
}
