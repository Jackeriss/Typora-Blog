const gulp = require('gulp')
const del = require('del')
const pump = require('pump')
const rev = require('gulp-rev')
const clean = require('gulp-clean-css')
const terser = require('gulp-terser')
const image = require('gulp-image')
const uploadQcloud = require('gulp-upload-qcloud')
const revCollector = require('gulp-rev-collector')
const config = require('./gulp.json')
const cos = require('./cos.json')

gulp.task('clean', function (cb) {
    del(config.clean.del, cb);
});

gulp.task('js', function (cb) {
    pump([
        gulp.src(config.js.src),
        rev(),
        terser(),
        gulp.dest(config.js.dest),
        rev.manifest(config.js.manifest),
        gulp.dest(config.revDest),
    ], cb)
});

gulp.task('css', function (cb) {
    pump([
        gulp.src(config.css.src),
        rev(),
        clean(),
        gulp.dest(config.css.dest),
        rev.manifest(config.css.manifest),
        gulp.dest(config.revDest),
    ], cb)
});

gulp.task('image', function (cb) {
    pump([
        gulp.src(config.image.src),
        rev(),
        image(),
        gulp.dest(config.image.dest),
        rev.manifest(config.image.manifest),
        gulp.dest(config.revDest),
    ], cb)
});

gulp.task('upload-js', ['js'], function (cb) {
    pump([
        gulp.src(config.uploadJs.src),
        uploadQcloud({
            AppId: cos.AppId,
            SecretId: cos.SecretId,
            SecretKey: cos.SecretKey,
            Bucket: cos.Bucket,
            Region: cos.Region,
            Prefix: config.uploadJs.prefix,
            OverWrite: cos.OverWrite
        })
    ], cb)
});

gulp.task('upload-css', ['css'], function (cb) {
    pump([
        gulp.src(config.uploadCss.src),
        uploadQcloud({
            AppId: cos.AppId,
            SecretId: cos.SecretId,
            SecretKey: cos.SecretKey,
            Bucket: cos.Bucket,
            Region: cos.Region,
            Prefix: config.uploadCss.prefix,
            OverWrite: cos.OverWrite
        })
    ], cb)
});

gulp.task('upload-image', ['image'], function (cb) {
    pump([
        gulp.src(config.uploadImage.src),
        uploadQcloud({
            AppId: cos.AppId,
            SecretId: cos.SecretId,
            SecretKey: cos.SecretKey,
            Bucket: cos.Bucket,
            Region: cos.Region,
            Prefix: config.uploadImage.prefix,
            OverWrite: cos.OverWrite
        })
    ], cb)
});

gulp.task('rev', ['upload-css', 'upload-js', 'upload-image'], function (cb) {
    pump([
        gulp.src(config.rev.src),
        revCollector(config.rev.revCollector),
        gulp.dest(config.rev.dest)
    ], cb)
});
 
gulp.task('default', ['clean', 'rev']);
