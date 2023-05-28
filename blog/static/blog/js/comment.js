$(() => {
    let csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    // Comment FORM
    $(document).on('click', '.add_comment', function (e) {
        e.preventDefault();
        let id = $(this).data('post_id');
        let comment = $('#add_comment_' + id).val();
        let url = $('#comment-form-' + id).attr('action');
        let post_data = {
            'text': comment,
            'csrfmiddlewaretoken': csrftoken,
        }
        if (comment === '') {
            alert('Please write a comment');
            return false;
        }
        console.log('add comment ', comment, ' for post id: ' + id, ' url: ' + url + ' post_data: ' + post_data)
        // post request to save comment
        $.post(url, post_data, (data, status) => {
            console.log(data);
            $('#comment_thread_' + id).html(data['html']);
            // comment_methods();
        });
    })
    // Reply Form
    $(document).on('click', '.add_reply', function (e) {
        e.preventDefault();
        let id = $(this).data('reply_id');
        let post_id = $(this).data('post_id');
        let reply = $('#add_reply_' + id).val();
        let url = $('#' + post_id + '-reply-form-' + id).attr('action');
        let post_data = {
            'reply_id': id,
            'text': reply,
            'csrfmiddlewaretoken': csrftoken,
        }
        if (reply === '') {
            alert('Please write a reply');
            return false;
        }
        console.log('add reply ', reply, ' for comment id: ' + id, ' url: ' + url + ' post_data: ' + post_data)
        $.post(url, post_data, (data, status) => {
            console.log(data);
            $('#comment_thread_' + post_id).html(data['html']);
            // comment_methods();
        });
    })

    $(document).on('click', '.reply', function (e) {
        e.preventDefault();
        let id = $(this).data('id');
        let post_id = $(this).data('post_id');
        $('#' + post_id + '-reply-form-' + id).toggleClass('d-none', 'd-block');
    })
})