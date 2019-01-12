$(function () {
  moment.locale('zh-cn');
  var time = $('.postBlock').find('.time');
  time.html(moment.unix(time.find('input').val()).fromNow());
  $('.achiveTime').each(function () {
    var timestamp = $(this).find('input').val();
    $(this).html(moment.unix(timestamp).format('LL'));
  });
  var loading = false,
    currentPage = 1,
    totalPage = $('.totalPage').val();
  if (totalPage) {
    if (totalPage == 0) {
      $('.postBlank').fadeIn(800, function () {
        $('.postBlank').removeClass('dn');
      });
    } else {
      $.ajax({
        type: 'get',
        url: '/postlist',
        data: {
          page: currentPage
        },
        dataType: 'json',
        success: function (data) {
          var post = '';
          for (var i = 0; i < data.length; i++) {
            post += ('<div class="postBlock">' + '<h2 class="title"><a href="/p/' + data[i].id +
              '">' + data[i].title + '</a></h2>' + '<div class="time">' +
              moment.unix(data[i].timestamp).fromNow() + '</div>' + data[i].abstract + '</div>')
          }
          $('#page1').html(post);
          $('#page1').removeClass('dn');
          $('.foot').removeClass('dn');
        }
      });
    }
  } else {
    $('.foot').removeClass('dn');
  }
  $(window).on('scroll', function () {
    var st = $(document).scrollTop();
    if (totalPage) {
      if (st == $(document).height() - $(window).height()) {
        if (loading == false) {
          loading = true;
          currentPage += 1;
          if (currentPage <= totalPage) {
            $('.loading').slideDown(300);
            setTimeout(function fade1() {
              $.ajax({
                type: 'get',
                url: '/postlist',
                data: {
                  page: currentPage
                },
                dataType: 'json',
                success: function (data) {
                  var post = '';
                  for (var i = 0; i < data.length; i++) {
                    post += ('<div class="postBlock">' + '<h2 class="title"><a href="/p/' + data[i].id +
                      '">' + data[i].title + '</a></h2>' + '<div class="time">' +
                      moment.unix(data[i].timestamp).fromNow() + '</div>' + data[i].abstract +
                      '</div>')
                  }
                  $('#page' + currentPage).html(post);
                  $('#page' + currentPage).removeClass('dn');
                }
              });
              $('.loading').slideUp(300);
              setTimeout(function fade2() {
                loading = false;
              }, 300);
            }, 1000);
          }
        }
      }
    }
    if (st > 500) {
      if ($('#main-container').length != 0) {
        var w = $(window).width(),
          mw = $('#main-container').width();
        if ((w - mw) / 2 > 70)
          $('#go-top').css({
            'left': (w - mw) / 2 + mw + 20
          });
        else {
          $('#go-top').css({
            'left': 'auto'
          });
        }
      }
      $('#go-top').fadeIn(800, function () {
        $(this).removeClass('dn');
      });
    } else {
      $('#go-top').fadeOut(800, function () {
        $(this).addClass('dn');
      });
    }
  });
  $('#go-top .go').on('click', function () {
    $('html,body').animate({
      'scrollTop': 0
    }, 500);
  });
  const gitalk = new Gitalk({
    clientID: '748b4dac7ace16b6d7cb',
    clientSecret: 'c5db352dad6f88b898840d628e44cfb5b4eaf4c0',
    repo: 'comments_of_www.jackeriss.com',
    owner: 'Jackeriss',
    admin: ['Jackeriss'],
    id: new Date().getTime(),
  })
  gitalk.render('gitalk-container')
});