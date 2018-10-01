var gulp = require('gulp'),
    del = require('del'),
    pump = require('pump'),
    rev = require('gulp-rev'),
    clean = require('gulp-clean-css'),
    terser = require('gulp-terser'),
    image = require('gulp-image'),
    revCollector = require('gulp-rev-collector');

gulp.task('clean', function (cb) {
    del([
        'dist/*',
        'src/template/prod/*',
    ], cb);
});

gulp.task('css', function (cb) {
    pump([
            gulp.src('src/static/css/*.css'),
            rev(),
            clean(),
            gulp.dest('dist'),
            rev.manifest({
                path: 'rev/rev-manifest.json',
                base: 'rev',
                merge: true
            }),
            gulp.dest('rev'),
        ], cb
    )
});
 
gulp.task('js', function (cb) {
    pump([
            gulp.src('src/static/js/*.js'),
            rev(),
            terser(),
            gulp.dest('dist'),
            rev.manifest({
                path: 'rev/rev-manifest.json',
                base: 'rev',
                merge: true
            }),
            gulp.dest('rev'),
        ], cb
    )
});

gulp.task('image', function (cb) {
    pump([
            gulp.src('src/static/image/*'),
            rev(),
            image(),
            gulp.dest('dist'),
            rev.manifest({
                path: 'rev/rev-manifest.json',
                base: 'rev',
                merge: true
            }),
            gulp.dest('rev'),
        ], cb
    )
});

gulp.task('rev', ['css', 'js', 'image'], function (cb) {
    pump([
            gulp.src(['rev/rev-manifest.json', 'src/template/dev/*.html']),
            revCollector({
                replaceReved: true,
                dirReplacements: {
                    '/css/': 'https://jackeriss-1252826939.file.myqcloud.com/css/',
                    '/js/': 'https://jackeriss-1252826939.file.myqcloud.com/js/',
                    '/image/': 'https://jackeriss-1252826939.file.myqcloud.com/image/',
                }
            }),
            gulp.dest('src/template/prod')
        ], cb
    )
});
 
gulp.task('default', ['clean', 'rev']);
