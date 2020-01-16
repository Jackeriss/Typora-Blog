const gulp = require('gulp');
const del = require('del')
const rev = require('gulp-rev')
const clean_css = require('gulp-clean-css')
const terser = require('gulp-terser')
const uploadQcloud = require('gulp-qcloud-cos-upload')
const revCollector = require('gulp-rev-collector')
const qcloud = require('./qcloud.json')
const cp = require("child_process")


gulp.task('clean', function (cb) {
  return del(['./dist'], cb)
})

gulp.task('build_js', function () {
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
})

gulp.task('build_css', function () {
  return gulp.src('app/static/css/*.css')
    .pipe(clean_css())
    .pipe(rev())
    .pipe(gulp.dest('dist'))
    .pipe(rev.manifest({
      path: 'dist/rev-manifest.json',
      base: 'dist',
      merge: true
    }))
    .pipe(gulp.dest('dist'))
})

gulp.task('upload', function () {
  return gulp.src('*.*', { cwd: 'dist' })
    .pipe(uploadQcloud({
      AppId: qcloud.AppId,
      SecretId: qcloud.SecretId,
      SecretKey: qcloud.SecretKey,
      Bucket: qcloud.Bucket,
      Region: qcloud.Region,
      prefix: qcloud.prefix
    }))
})

gulp.task('rev_collect', function () {
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
})

gulp.task('install', function () {
  return cp.exec('pipenv install --deploy')
})

gulp.task('start', function () {
  return cp.exec('/usr/local/bin/pm2 startOrReload pm2.json')
})

exports.default = gulp.series('clean', gulp.parallel('build_js', 'build_css'), 'upload', 'rev_collect', 'install', 'start')
