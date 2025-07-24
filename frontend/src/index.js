import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';
import $ from 'jquery';


function getCookie(name) {
  let cookieValue = null;
  document.cookie.split(';').forEach(c => {
    const [k, v] = c.trim().split('=');
    if (k === name) cookieValue = decodeURIComponent(v);
  });
  return cookieValue;
}
$(document).on('click', '.like-btn', function() {
  const btn = $(this);
  $.ajax({
    url: btn.data('url'),
    method: 'POST',
    headers: {'X-CSRFToken': getCookie('csrftoken')},
    success: data => {
      btn.text(data.liked ? 'Unlike' : 'Like');
      btn.toggleClass('btn-danger', data.liked);
      btn.toggleClass('btn-outline-primary', !data.liked);
      btn.closest('.post-actions').find('.like-count').text(data.likes_count);
    }
  });
});

$(document).on('click', '.follow-btn', function() {
  const btn = $(this);
  $.ajax({
    url: btn.data('url'),
    method: 'POST',
    headers: {'X-CSRFToken': getCookie('csrftoken')},
    success: data => {
      btn.text(data.is_following ? 'Unsubscribe' : 'Subscribe');
      btn.toggleClass('btn-primary', !data.is_following);
      btn.toggleClass('btn-outline-secondary', data.is_following);
      $('.followers-count').text(data.followers_count);
    }
  });
});

