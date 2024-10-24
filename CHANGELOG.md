## 2.1.0 - Released on 2024-10-24

* Now configuration can contains environment variable that

  will be replaced before configurating the app.
  * Only ${VARIABLE} will be replaced if present in the os.environ
  * A default value can be specified using ${VARIABLE-default-value}

This feature is great at injecting secrets in the configuration
and keep code simple.

* A `--yaml-key` has been added to configure the celery configuration dict.
  by default its still `celery`.


## 2.0.0 - Released on 2024-10-24
* Drop support of python < 3.9
* Drop support of Celery 4

## 1.0.2 - Released on 2023-10-24
* Remove the bootstep for celery 5, it just not works.

## 1.0.1 - Released on 2023-10-18

* Tests with celery 5, keep celery 4 

## 1.0.0 - Released on 2023-02-02

* Improve typing
* Add continuous integration

## Version 0.4.0 - 2022-01-20

* Add an optional on_yaml_loaded event on the app.

## Version 0.3.0 - 2022-01-20

* Update dependencies

## Version 0.2.3 - 2021-04-28

 * Fix packaging
 * Add tests and examples

## Version 0.1.3 - 2021-04-27

 * Initial release
