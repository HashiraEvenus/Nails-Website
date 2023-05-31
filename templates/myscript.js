$( function() {
    $( "#datepicker" ).datepicker({ minDate: -20, maxDate: "+1M +10D" });
  } );
$("input.DateFrom").datepicker({
    minDate: 0
});