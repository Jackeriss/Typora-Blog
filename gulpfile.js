const { src, dest, series, parallel } = require('gulp');
const del = require('del')
const rev = require('gulp-rev')
const clean_css = require('gulp-clean-css')
const terser = require('gulp-terser')
const image = require('gulp-image')
const uploadQcloud = require('gulp-qcloud-cos-upload')
const revCollector = require('gulp-rev-collector')
const qcloud = require('./qcloud.json')

function clean(cb) {
  return del(['./dist'], cb)
}

function build_js() {
  return src('app/static/js/*.js')
    .pipe(terser())
    .pipe(rev())
    .pipe(dest('dist'))
    .pipe(rev.manifest({
      path: 'dist/rev-manifest.json',
      base: 'dist',
      merge: true
    }))
    .pipe(dest('dist'))
}

function build_css() {
  return src('app/static/css/*.css')
    .pipe(clean_css())
    .pipe(rev())
    .pipe(dest('dist'))
    .pipe(rev.manifest({
      path: 'dist/rev-manifest.json',
      base: 'dist',
      merge: true
    }))
    .pipe(dest('dist'))
}

function build_image() {
  return src('app/static/image/*.*')
    .pipe(image())
    .pipe(rev())
    .pipe(dest('dist'))
    .pipe(rev.manifest({
      path: 'dist/rev-manifest.json',
      base: 'dist',
      merge: true
    }))
    .pipe(dest('dist'))
}

function upload() {
  return src('*.*', {cwd: 'dist'})
    .pipe(uploadQcloud({
      AppId: qcloud.AppId,
      SecretId: qcloud.SecretId,
      SecretKey: qcloud.SecretKey,
      Bucket: qcloud.Bucket,
      Region: qcloud.Region,
      prefix: qcloud.prefix
    }))
}

function rev_collect() {
  return src(['dist/rev-manifest.json', 'app/template/*.html'])
    .pipe(revCollector({
      'replaceReved': true,
      'dirReplacements': {
        '/css/': 'https://jackeriss-1252826939.file.myqcloud.com/' + qcloud.prefix + '/',
        '/js/': 'https://jackeriss-1252826939.file.myqcloud.com/' + qcloud.prefix + '/',
        '/image/': 'https://jackeriss-1252826939.file.myqcloud.com/' + qcloud.prefix + '/'
      }
    }))
    .pipe(dest('app/template/dist'))
}

exports.default = series(clean, parallel(build_js, build_css, build_image), upload, rev_collect)
