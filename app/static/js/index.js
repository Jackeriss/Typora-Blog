$(function () {
  window.parent.history.pushState({}, document.title, window.location.href.replace('/i/', '/'))
  moment.locale('zh-cn')
  let time = $('.postBlock').find('.time')
  time.html(moment.unix(time.find('input').val()).fromNow())
  $('.achiveTime').each(function () {
    let timestamp = $(this).find('input').val()
    $(this).html(moment.unix(timestamp).format('LL'))
  })
  let loading = false,
    currentPage = 1,
    totalPage = $('.totalPage').val()
  if (totalPage) {
    if (totalPage == 0) {
      $('.postBlank').fadeIn(800, function () {
        $('.postBlank').removeClass('dn')
      })
    } else {
      $.ajax({
        type: 'get',
        url: '/v1/posts',
        data: {
          page: currentPage
        },
        dataType: 'json',
        success: function (data) {
          let post = ''
          for (let i in data.body) {
            post += ('<div class="postBlock">' + '<h2 class="title"><a href="/post/' + data.body[i].id +
              '">' + data.body[i].title + '</a></h2>' + '<div class="time">' +
              moment.unix(data.body[i].timestamp).fromNow() + '</div>' + data.body[i].abstract + '</div>')
          }
          $('#page1').html(post)
          $('#page1').removeClass('dn')
          $('.foot').removeClass('dn')
        }
      })
    }
  } else {
    $('.foot').removeClass('dn')
  }
  $(window).on('scroll', function () {
    let st = $(document).scrollTop()
    if (totalPage) {
      if (st == $(document).height() - $(window).height()) {
        if (loading == false) {
          loading = true
          currentPage += 1
          if (currentPage <= totalPage) {
            $('.loading').slideDown(300)
            setTimeout(function fade1() {
              $.ajax({
                type: 'get',
                url: '/v1/posts',
                data: {
                  page: currentPage
                },
                dataType: 'json',
                success: function (data) {
                  let post = ''
                  for (let i in data.body) {
                    post += ('<div class="postBlock">' + '<h2 class="title"><a href="/post/' + data.body[i].id +
                      '">' + data.body[i].title + '</a></h2>' + '<div class="time">' +
                      moment.unix(data.body[i].timestamp).fromNow() + '</div>' + data.body[i].abstract +
                      '</div>')
                  }
                  $('#page' + currentPage).html(post)
                  $('#page' + currentPage).removeClass('dn')
                }
              })
              $('.loading').slideUp(300)
              setTimeout(function fade2() {
                loading = false
              }, 300)
            }, 1000)
          }
        }
      }
    }
    if (st > 500) {
      if ($('#main-container').length != 0) {
        let w = $(window).width(),
          mw = $('#main-container').width()
        if ((w - mw) / 2 > 70)
          $('#go-top').css({
            'left': (w - mw) / 2 + mw + 20
          })
        else {
          $('#go-top').css({
            'left': 'auto'
          })
        }
      }
      $('#go-top').fadeIn(800, function () {
        $(this).removeClass('dn')
      })
    } else {
      $('#go-top').fadeOut(800, function () {
        $(this).addClass('dn')
      })
    }
  })
  $('#go-top .go').on('click', function () {
    $('html,body').animate({
      'scrollTop': 0
    }, 500)
  })
  const gitalk = new Gitalk({
    clientID: 'f97829d37a8d54c05536',
    clientSecret: '89896e7c2dc8eaf50f8b86baabc50005833a3062',
    repo: 'comments_of_www.jackeriss.com',
    owner: 'Jackeriss',
    admin: ['Jackeriss'],
    id: document.title.split(' - ')[0],
  })
  gitalk.render('gitalk-container')
})