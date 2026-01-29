<!-- Source: Labelary API Documentation -->
<!-- Section: Programming Language Examples -->
<!-- Generated: 2025-11-02 19:43:59 -->

# 5. Examples (Programming Languages)

## 5.8. Java Example

A Java example that uses the Java 11 HttpClient API to send a POST request to convert a ZPL string to a PDF file:

```java
var zpl = "^xa^cfa,50^fo100,100^fdHello World^fs^xz";

// adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
var uri = URI.create("http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/");
var request = HttpRequest.newBuilder(uri)
    .header("Accept", "application/pdf") // omit this line to get PNG images back
    .POST(BodyPublishers.ofString(zpl))
    .build();
var client = HttpClient.newHttpClient();
var response = client.send(request, BodyHandlers.ofByteArray());
var body = response.body();

if (response.statusCode() == 200) {
    var file = new File("label.pdf"); // change file name for PNG images
    Files.write(file.toPath(), body);
} else {
    var errorMessage = new String(body, StandardCharsets.UTF_8);
    System.out.println(errorMessage);
}
```

## 5.9. Python Example

A Python example that uses the Requests library to send a POST request to convert a ZPL string to a PDF file:

```python
import requests
import shutil

zpl = '^xa^cfa,50^fo100,100^fdHello World^fs^xz'

# adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
files = {'file' : zpl}
headers = {'Accept' : 'application/pdf'} # omit this line to get PNG images back
response = requests.post(url, headers = headers, files = files, stream = True)

if response.status_code == 200:
    response.raw.decode_content = True
    with open('label.pdf', 'wb') as out_file: # change file name for PNG images
        shutil.copyfileobj(response.raw, out_file)
else:
    print('Error: ' + response.text)
```

## 5.10. Ruby Example

A Ruby example that uses a POST request to convert a ZPL string to a PDF file (courtesy Robert Coleman):

```ruby
require 'net/http'

zpl = '^xa^cfa,50^fo100,100^fdHello World^fs^xz'

# adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
uri = URI 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
http = Net::HTTP.new uri.host, uri.port
request = Net::HTTP::Post.new uri.request_uri
request.body = zpl
request['Accept'] = 'application/pdf' # omit this line to get PNG images back
response = http.request request

case response
when Net::HTTPSuccess then
    File.open 'label.pdf', 'wb' do |f| # change file name for PNG images
        f.write response.body
    end
else
    puts "Error: #{response.body}"
end
```

## 5.11. Node.js Example

A Node.js example that uses a POST request to convert a ZPL string to a PDF file (courtesy Katy LaVallee):

```javascript
var fs = require('fs');
var request = require('request');

var zpl = "^xa^cfa,50^fo100,100^fdHello World^fs^xz";

var options = {
    encoding: null,
    formData: { file: zpl },
    // omit this line to get PNG images back
    headers: { 'Accept': 'application/pdf' },
    // adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
    url: 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
};

request.post(options, function(err, resp, body) {
    if (err) {
        return console.log(err);
    }
    var filename = 'label.pdf'; // change file name for PNG images
    fs.writeFile(filename, body, function(err) {
        if (err) {
            console.log(err);
        }
    });
});
```

## 5.12. D Language Example

A D language example that uses a POST request to convert a ZPL string to a PDF file (courtesy Andrea Freschi):

```d
import std.stdio;
import std.net.curl;

// adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
auto url = "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/";
auto zpl = "^xa^cfa,50^fo100,100^fdHello World^fs^xz";

void main() {
    auto conn = HTTP();
    conn.addRequestHeader("Accept", "application/pdf"); // omit this line to get PNG images back
    auto label = url.post!ubyte(zpl, conn);
    if (conn.statusLine.code == 200) {
        label.toFile("label.pdf"); // change file name for PNG images
    } else {
        writeln(conn.statusLine.toString());
    }
}
```

## 5.13. C# Example

A C# example that uses a POST request to convert a ZPL string to a PDF file:

```csharp
byte[] zpl = Encoding.UTF8.GetBytes("^xa^cfa,50^fo100,100^fdHello World^fs^xz");

// adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
var request = (HttpWebRequest) WebRequest.Create("http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/");
request.Method = "POST";
request.Accept = "application/pdf"; // omit this line to get PNG images back
request.ContentType = "application/x-www-form-urlencoded";
request.ContentLength = zpl.Length;

var requestStream = request.GetRequestStream();
requestStream.Write(zpl, 0, zpl.Length);
requestStream.Close();

try {
    var response = (HttpWebResponse) request.GetResponse();
    var responseStream = response.GetResponseStream();
    var fileStream = File.Create("label.pdf"); // change file name for PNG images
    responseStream.CopyTo(fileStream);
    responseStream.Close();
    fileStream.Close();
} catch (WebException e) {
    Console.WriteLine("Error: {0}", e.Status);
}
```

## 5.14. VB.NET Example

A VB.NET example that uses a POST request to convert a ZPL string to a PDF file:

```vb
Dim zpl() As Byte = Encoding.UTF8.GetBytes("^xa^cfa,50^fo100,100^fdHello World^fs^xz")

' adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
Dim request As HttpWebRequest = WebRequest.Create("http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/")
request.Method = "POST"
request.Accept = "application/pdf" ' omit this line to get PNG images back
request.ContentType = "application/x-www-form-urlencoded"
request.ContentLength = zpl.Length

Dim requestStream As Stream = request.GetRequestStream()
requestStream.Write(zpl, 0, zpl.Length)
requestStream.Close()

Try
    Dim response As HttpWebResponse = request.GetResponse()
    Dim responseStream As Stream = response.GetResponseStream()
    Dim fileStream As Stream = File.Create("label.pdf") ' change file name for PNG images
    responseStream.CopyTo(fileStream)
    responseStream.Close()
    fileStream.Close()
Catch e As WebException
    Console.WriteLine("Error: {0}", e.Status)
End Try
```

## 5.15. Rust Example

A Rust example that uses Reqwest to send a POST request to convert a ZPL string to a PDF file:

```rust
use reqwest::Client;
use std::io::Cursor;
use std::fs::File;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {

    let zpl = "^xa^cfa,50^fo100,100^fdHello World^fs^xz";

    // adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
    let url = "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/";
    let response = Client::new()
        .post(url)
        .body(zpl)
        .header("Accept", "application/pdf") // omit this line to get PNG images back
        .send().await?;

    if response.status().is_success() {
        let mut file = File::create("label.pdf")?; // change file name for PNG images
        let mut content = Cursor::new(response.bytes().await?);
        std::io::copy(&mut content, &mut file)?;
    } else {
        let error_message = response.text().await?;
        eprintln!("{}", error_message);
    }

    Ok(())
}
```

## 5.16. Go Language Example

A Go language example that uses a POST request to convert a ZPL string to a PDF file:

```go
package main

import (
    "os"
    "io"
    "io/ioutil"
    "log"
    "bytes"
    "net/http"
)

func main() {

    zpl := []byte("^xa^cfa,50^fo100,100^fdHello World^fs^xz")
    // adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
    req, err := http.NewRequest("POST", "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/", bytes.NewBuffer(zpl))
    if err != nil {
        log.Fatalln(err)
    }
    req.Header.Set("Accept", "application/pdf") // omit this line to get PNG images back

    client := &http.Client{}
    response, err := client.Do(req)
    if err != nil {
        log.Fatalln(err)
    }
    defer response.Body.Close()

    if response.StatusCode == http.StatusOK {
        file, err := os.Create("label.pdf") // change file name for PNG images
        if err != nil {
            log.Fatalln(err)
        }
        defer file.Close()
        io.Copy(file, response.Body)
    } else {
        body, err := ioutil.ReadAll(response.Body)
        if err != nil {
            log.Fatalln(err)
        }
        log.Fatalln(string(body))
    }
}
```