# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline


class BangbrosArtistsPipeline:
    def process_item(self, item, spider):
        return item


class RenameImagesPipeline(ImagesPipeline):  

    #Name download version
    def file_path(self, request, response=None, info=None, *, item=None): 
        ordner = item.get('name', '')
        file = item.get('image_name', '')        
        return f"{ordner}/{file}.jpg"  