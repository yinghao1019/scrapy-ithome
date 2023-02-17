# scrapy-docker
### Introduction
This is dokcer image for build image.
Additional,when you run below step,you should set .env 
in project root directory

### Quick start(Deploy to scrapyd)
1. Clone the repo and get into the folder
```
$ cd scrapy-ithome
```
2. Use pipenv to build virtualenv
```
$ pipenv install
```
3. use command to eggifying and deploy to scrapyd addversion.json endpoint
```
$ scrapyd-deploy local -p ithome -v <version> --include-dependencies
```
If successful you should see a JSON response similar to the following:
```
Deploying myproject-1287453519 to http://localhost:6800/addversion.json
Server response (200):
{"status": "ok", "spiders": ["spider1", "spider2"]}
```

4. check project status
```
$ curl http://localhost:6800/listspiders.json?project=ithome
```
successful response
```
{"status": "ok", "spiders": ["spider1", "spider2", "spider3"]}
```
5. run spider(set mongo db connection),run spider args(start_url,start_page,crawl_pages)
```
$ curl http://localhost:6800/schedule.json -d project=ithome -d spider=ithome_theme setting=<mongo db connection>
```
successful response
```
{"status": "ok", "jobid": "6487ec79947edab326d6db28a2d86511e8247444"}
```
6.check job status
```
$ curl http://localhost:6800/listjobs.json?project=myproject
```

successful response
```
$ {
    "status": "ok",
    "pending": [
        {
            "project": "myproject", "spider": "spider1",
            "id": "78391cc0fcaf11e1b0090800272a6d06"
        }
    ],
    "running": [
        {
            "id": "422e608f9f28cef127b3d5ef93fe9399",
            "project": "myproject", "spider": "spider2",
            "start_time": "2012-09-12 10:14:03.594664"
        }
    ],
    "finished": [
        {
            "id": "2f16646cfcaf11e1b0090800272a6d06",
            "project": "myproject", "spider": "spider3",
            "start_time": "2012-09-12 10:14:03.594664",
            "end_time": "2012-09-12 10:24:03.594664",
            "log_url": "/logs/myproject/spider3/2f16646cfcaf11e1b0090800272a6d06.log",
            "items_url": "/items/myproject/spider3/2f16646cfcaf11e1b0090800272a6d06.jl"
        }
    ]
}
```

### Reference
* scarpyd offical api([傳送門](https://scrapyd.readthedocs.io/en/stable/api.html))
* scarpyd client([傳送門](https://github.com/scrapy/scrapyd-client))
* scrapy ([傳送門](https://docs.scrapy.org/en/latest/))