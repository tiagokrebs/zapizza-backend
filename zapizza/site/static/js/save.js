$('#addRua').click(function(e) {
        e.preventDefault();
        $('#modal').modal();
    });
	
	


$('#ruasubmit').on('click', function(e) {
    e.preventDefault();
    $.ajax({
        type: "POST",

        data: $('form.LogradouroForm'),
        success: function(response) {
            alert(response['response']);
        },
        error: function() {
            alert('Error');
        }
    });
    return false;
});

$.ajaxSetup({
  data: {csrfmiddlewaretoken: '{{ csrf_token }}' },
});