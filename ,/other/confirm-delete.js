
	$('.fancybox-confirm-delete').fancybox({
	    modal:true,
	})

	$(".fancybox-confirm-delete").on('click',function(){
    	$('#delete-target').html($(this).data('delete-target'))
    	$('#delete-form').attr('action', $(this).data('target-url'))
	})

	$('#confirm-delete-close').on('click',function(){
		$.fancybox.close()
		return false
	})