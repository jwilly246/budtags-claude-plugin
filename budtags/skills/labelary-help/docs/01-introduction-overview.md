<!-- Source: Labelary API Documentation -->
<!-- Section: Introduction and Overview -->
<!-- Generated: 2025-11-02 19:43:59 -->

# 1. Introduction

The Labelary ZPL rendering engine is available as an online service, and can be invoked via a simple, easy-to-use RESTful API:

```
GET http://api.labelary.com/v1/printers/{dpmm}/labels/{width}x{height}/{index}/{zpl}
```

By default the service returns PNG images, but a variety of output formats are available:

- **PNG** (requested by sending an `Accept: image/png` request header, or by omitting the Accept request header entirely)
- **PDF** (requested by sending an `Accept: application/pdf` request header)
- **IPL** (requested by sending an `Accept: application/ipl` request header)
- **EPL** (requested by sending an `Accept: application/epl` request header)
- **DPL** (requested by sending an `Accept: application/dpl` request header)
- **SBPL** (requested by sending an `Accept: application/sbpl` request header)
- **PCL 5** (requested by sending an `Accept: application/pcl5` request header)
- **PCL 6** (requested by sending an `Accept: application/pcl6` request header)
- **JSON** (requested by sending an `Accept: application/json` request header, useful for data extraction)

```
POST http://api.labelary.com/v1/printers/{dpmm}/labels/{width}x{height}/{index}
```

You can also use POST instead of GET by moving the ZPL out of the URL and into the POST request body. When using POST, the request Content-Type may be either:

- `application/x-www-form-urlencoded` (in which case the request body should contain the raw ZPL to be converted), or
- `multipart/form-data` (in which case the ZPL should be provided in a form parameter named `file`)

See below for examples of both approaches.

## When to Use POST

The POST HTTP method is useful when:

- Your ZPL is very large (since URLs are limited to roughly 3,000 characters), or
- You are running into character encoding issues, or
- Your ZPL contains embedded binary data, or
- Your ZPL contains sensitive information (since URLs may be logged by proxies and other intermediaries)