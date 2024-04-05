from multiprocessing import Process, Manager, freeze_support
from PyQt6.QtCore import QThread

class ScraperThread(QThread):
    def __init__(self, MainWindow):
        super(LogThread, self).__init__()
        self.Main = MainWindow

    def run(self) -> None:
        while True:
            if not self.Main.Q.empty():
                record = self.Main.Q.get()

                if record['type'] == 4:
                    self.Main.btnSearch.setText('Start Search')
                    break

                data = record['data']
                id = data['id']
                if record['type'] == 1:
                    row = self.Main.tableViewResult.model().rowCount()
                    data['rowNum'] = row
                    self.Main.database[id] = data

                    if self.Main.targetUrl not in data['pdpUrl']:
                        data['pdpUrl'] = self.Main.targetUrl + data['pdpUrl']

                        if data["minPrice"] == 0:
                            minPrice = 'Any'
                        else:
                            minPrice = data["minPrice"]

                        if data["maxPrice"] == 0:
                            maxPrice = 'Any'
                        else:
                            maxPrice = data["maxPrice"]

        #header_labels = ["ID", "Title", "Date Updated", "Street", "Suburb", "State", "Postcode", "Price", "Price Range", "Agency Company", "Agency Contact", "Property", "Land Area", "Floor Area", "Carspaces"]
                    self.Main.tableViewResult.model().insertRow(
                        row,
                        [
                            # ID
                            QStandardItem(data['id']),
                            # Title
                            QStandardItem(isset('title', data)),
                            # Date Updated
                            QStandardItem(""),
                            # Street
                            QStandardItem(
                                isset('streetAddress', data['address'])),
                            # Suburb
                            QStandardItem(""),
                            # State
                            QStandardItem(""),
                            # Postcode
                            QStandardItem(""),
                            # Price Posted
                            QStandardItem(isset('price', data['details'])),
                            # Approx. Price Range
                            QStandardItem(
                                f'{minPrice} - {maxPrice}'),
                            # Agency Comp.
                            QStandardItem(
                                data['agencies'][0]['name']),
                            # Agency Contact
                            QStandardItem(""),
                            # Property Type
                            QStandardItem(
                                ", ".join(data['attributes']['propertyTypes'])),
                            # Land Area
                            QStandardItem(""),
                            # Floor Area
                            QStandardItem(data['attributes']['area']),
                            # Car spaces
                            QStandardItem(""),
                            # Highlights
                            QStandardItem(""),
                            # Description
                            QStandardItem(""),
                            # Link
                            QStandardItem(data['pdpUrl']),
                        ]
                    )
                elif record['type'] == 2:
                    data = record['data']
                    rowNum = self.Main.database[id]['rowNum']

                    updatedAt = data['lastUpdatedAt']
                    address = data['address']
                    street = address["streetAddress"]
                    suburb = address["suburb"]
                    state = address["state"]
                    postcode = address["postcode"]
                    uid = re.sub(r'[^a-zA-Z0-9]', '',
                                 street)[:4] + suburb[:2] + state[:2]

                    if updatedAt <= self.Main.datefrom or updatedAt >= self.Main.dateto + "T23:59:59Z":
                        self.Main.tableViewResult.setRowHidden(rowNum, True)

                    self.Main.database[id]['detail'] = data
                    self.Main.database[id]['uid'] = uid

                    self.Main.tableViewResult.model().item(
                        rowNum, 2).setText(updatedAt)
                    self.Main.tableViewResult.model().item(
                        rowNum, 4).setText(suburb)
                    self.Main.tableViewResult.model().item(
                        rowNum, 5).setText(state)
                    self.Main.tableViewResult.model().item(
                        rowNum, 6).setText(postcode)

                    for attr in data['attributes']:
                        if attr['id'] == "floor-area":
                            self.Main.tableViewResult.model().item(
                                rowNum, 13).setText(attr["value"])
                        elif attr['id'] == "land-area":
                            self.Main.tableViewResult.model().item(
                                rowNum, 12).setText(attr["value"])
                        elif attr['id'] == "car-spaces":
                            self.Main.tableViewResult.model().item(
                                rowNum, 14).setText(attr["value"])

                    if len(data["agencies"]) and "salespeople" in data["agencies"][0] and len(data["agencies"][0]["salespeople"]):
                        salespeople = data['agencies'][0]["salespeople"]
                        contacts = ""
                        for contact in salespeople:
                            contacts += f'{contact["name"]} : {contact["phone"]["display"]}' + " "
                        self.Main.tableViewResult.model().item(
                            rowNum, 10).setText(contacts)

                    self.Main.tableViewResult.model().item(
                        rowNum, 15).setText("\n".join(data['highlights']))
                    self.Main.tableViewResult.model().item(
                        rowNum, 16).setText(data['description'].replace("<br/>", "\n"))

                elif record['type'] == 3:
                    try:
                        data = record['data']
                        rowNum = self.Main.database[id]['rowNum']
                        self.Main.database[id]['minPrice'] = data['minPrice']
                        self.Main.database[id]['maxPrice'] = data['maxPrice']

                        if data["minPrice"] == 0:
                            minPrice = 'Any'
                        else:
                            minPrice = data["minPrice"]

                        if data["maxPrice"] == 0:
                            maxPrice = 'Any'
                        else:
                            maxPrice = data["maxPrice"]

                        self.Main.tableViewResult.model().item(
                            rowNum, 8).setText(f'{minPrice} - {maxPrice}')
                    except Exception as e:
                        # Handle other exceptions (generic Exception class)
                        print("An error occurred")
                        print(f"Error details: {e}")

                self.msleep(20)


def crawl_run(Q, url, dataset, isLease):
    # CrawlerProcess
    settings = get_project_settings()

    process = CrawlerProcess(settings=settings)
    process.crawl(scrapspider, Q=Q, base_url=url,
                  dataset=dataset, isLease=isLease)
    process.start()

    """
    # CrawlerRunner
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='output.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
    runner = CrawlerRunner(settings={
        'USER_AGENT': ua,
        'ROBOTSTXT_OBEY': is_obey,
        'SAVE_CONTENT': 'scraps.jl',
        'ITEM_PIPELINES': {
            'scraps.pipelines.ChanelPipeline': 300,
        },
    })
    d = runner.crawl(scrapspider, Q=Q)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    """


if __name__ == '__main__':
    freeze_support()
    app = QApplication(sys.argv)
    scraps = CrawlWindows()
    scraps.show()
    sys.exit(app.exec_())
