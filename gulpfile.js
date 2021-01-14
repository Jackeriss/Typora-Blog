const gulp = require('gulp');
const del = require('del')
const rev = require('gulp-rev')
const cleanCss = require('gulp-clean-css')
const terser = require('gulp-terser')
const uploadQcloud = require('gulp-qcloud-cos-upload')
const revCollector = require('gulp-rev-collector')
const qcloud = require('./qcloud.json')
const run = require('gulp-run')


function clean(cb) {
  return del(['./dist'], cb)
}

function build_js() {
  return gulp.src('app/static/js/*.js')
    .pipe(terser())
    .pipe(rev())
    .pipe(gulp.dest('dist'))
    .pipe(rev.manifest({
      path: 'dist/rev-manifest.json',
      base: 'dist',
      merge: true
    }))
    .pipe(gulp.dest('dist'))
}

function build_css() {
  return gulp.src('app/static/css/*.css')
    .pipe(cleanCss({ inline: ['none'] }))
    .pipe(rev())
    .pipe(gulp.dest('dist'))
    .pipe(rev.manifest({
      path: 'dist/rev-manifest.json',
      base: 'dist',
      merge: true
    }))
    .pipe(gulp.dest('dist'))
}

function upload() {
  return gulp.src('*.*', { cwd: 'dist' })
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
  return gulp.src(['dist/rev-manifest.json', 'app/template/*.html'])
    .pipe(revCollector({
      'replaceReved': true,
      'dirReplacements': {
        '/css/': 'https://jackeriss-1252826939.file.myqcloud.com/' + qcloud.prefix + '/',
        '/js/': 'https://jackeriss-1252826939.file.myqcloud.com/' + qcloud.prefix + '/',
        '/image/': 'https://jackeriss-1252826939.file.myqcloud.com/' + qcloud.prefix + '/'
      }
    }))
    .pipe(gulp.dest('app/template/dist'))
}

function start() {
  return run('/usr/local/bin/pm2 startOrRestart pm2.json').exec()
}

exports.default = gulp.series(
  clean,
  gulp.parallel(build_js, build_css),
  upload,
  rev_collect,
  start
)
