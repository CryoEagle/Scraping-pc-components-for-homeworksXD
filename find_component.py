from bs4 import BeautifulSoup
import requests

class Search_enum:
    SSD = "SSD"
    Motherboard = "Základová deska"
    Procesor = "Procesor"

class SSD:
    def __init__(self, capacity = 0, speed_read = 0, speed_write = 0):
        self.Capacity = capacity
        self.Speed_read = speed_read
        self.Speed_write = speed_write

class Motherboard:
    def __init__(self, patice, chipset, mFormat):
        self.Patice = patice
        self.Chipset = chipset
        self.Format = mFormat

class Procesor:
    def __init__(self, patice, gen, cores, threads, frequenc, turbo, tdp, chipset):
        self.Patice = patice
        self.Gen = gen
        self.Cores = cores
        self.Threads = threads
        self.Frequenc = frequenc
        self.Turbo = turbo
        self.Tdp = tdp
        self.Chipset = chipset

class Component:
    def __init__(self, name, url, id, price, comp_name, comp_obj):
        self.Price = price
        self.Comp_name = comp_name
        self.Comp_obj = comp_obj
        self.Url = url
        self.ID = id
        self.Product_name = name

class Component_scrap_core:
    selected_motherboard = None

    def check_proc_compatibility_w_motherboard(self, procesor: Procesor):
        result = True

        if self.selected_motherboard.Comp_obj.Patice != procesor.Patice:
            print("1. Test patice neprošel")
            result = False
        else:
            print("1. Test patice prošel")

        if procesor.Chipset.find(self.selected_motherboard.Comp_obj.Chipset) == -1:
            print("2. Test chipsetu neprošel")
            result = False
        else:
            print("2. Test chipsetu prošel")

        
        return result

    def search_components_by_compName(self, pageUrl, compName, how_many_products_fetch, architectureType = "all"):
        print("vyhledávám: " + compName)

        componentsFound = []

        processed_comps_iteration = 0
        iteration = 0
        last_page = 0

        while len(componentsFound) < how_many_products_fetch:
            notCompatibleItems = 0


            if processed_comps_iteration != 0:
                print("Některá data musela být vyhozena, proto sbíráme další data")
                how_many_products_fetch = how_many_products_fetch - len(componentsFound)
            processed_comps_iteration += 1
            if pageUrl == "https://www.czc.cz/":
                page = None
                if last_page == 0:
                    page = requests.get(pageUrl + compName + "/hledat") # stránka s produkty
                else:
                    page = requests.get(pageUrl + compName + "/hledat?q-first="+str(last_page))
                soup = BeautifulSoup(page.content, 'html.parser') # parsnutí do zpracovatelné formy

                job_elems = soup.find_all('div', class_='new-tile') # vezmeme array produktů (html element)
                
                print("dosažený počet produktů: " + str(len(job_elems)))
                
                if len(job_elems) > how_many_products_fetch:
                    print("Přesažený počet produktů - zkracuji")
                    for i in range(0, len(job_elems) - how_many_products_fetch): 
                        job_elems.pop()

                while len(job_elems) < how_many_products_fetch:
                    print("nedosažený počet potřebných produktů, opakuji request")
                    another_page = requests.get(pageUrl + compName + "/hledat?q-first=" + str(len(job_elems) + last_page))
                    soup_another_page = BeautifulSoup(another_page.content, 'html.parser')
                    job_elems_another_page = soup_another_page.find_all('div', class_='new-tile')
                    for job_elem in job_elems_another_page:
                        if len(job_elems) < how_many_products_fetch:
                            job_elems.append(job_elem)
                        else:
                            print("dosažený počet produktů: " + str(len(job_elems)))
                            break

                print("\r\nSbírám specifikace " + compName)

                for job_elem in job_elems: # projíždíme produkty
                    iteration += 1
                    product_name = job_elem.find(class_ = "tile-title").text.strip()
                    url_to_specifications = job_elem.find(class_ = "tile-link") # vyhledáme odkaz na produkt
                    url_to_specifications = url_to_specifications.get("href") # vezmeme hodnotu attributu href
                    
                    spec_page_url = pageUrl + url_to_specifications[1:] # stránka se specifikací
                    spec_page = requests.get(spec_page_url) # pošleme request
                    soup_spec = BeautifulSoup(spec_page.content, 'html.parser') # parsneme do zpracovatelné formy

                    # cena
                    price = soup_spec.find(class_ = "total-price") # najdeme cenu
                    price_final = str(price.find(class_ = "price-vatin").text) # vezmeme text uvnitř komponentu s cenou

                    # extrakce parametrů do array
                    paramsArray = []

                    def add_params_to_array(index_of_params):
                        params = soup_spec.findAll(class_ = "pd-parameter-item")[index_of_params] # vezmeme element obsahující všechny technický parametry

                        first_param = params.find("p") # vezmeme první parametr
                        paramsArray.append(first_param) # přidáme do array parametrů
                        first_param_siblings = first_param.find_next_siblings("p") # vezmeme všechny sousedící parametry s prvním parametrem
                        for sibling in first_param_siblings: # sousedící parametry iterujeme a přidáme do array parametrů
                            paramsArray.append(sibling)

                    add_params_to_array(0)

                    # vrátí hodnotu parametru, pokud nic nenajde vrátí None
                    def get_only_param_val(index):
                        paramVal = paramsArray[index].find("strong")
                        if paramVal != None:
                            return paramVal.text.strip()
                        else:
                            return None

                    component_object = None # Komponent (SSD, Motherboard, Zdroj...)

                    # pokud nenastane chyba při získávání parametrů vypíšeme obecné informace o produktu
                    # v listu základovek k ID je vynechaná jedna nebo více iterací z důvodu chyby, vyrovnání nelze z důvodu vyčkávání na response webu
                    def print_general_info():
                        print("\r\nID: " + str(iteration) + " " + compName + " produkt:") 
                        print("\tNázev: " + product_name)
                        print("\tOdkaz: " + spec_page_url)
                        print("\tCena: " + price_final)


                    try:
                        if compName == Search_enum.SSD:
                            # 2 = kapacita  4 = rychlost čtení 5 = rychlost zápisu
                            component_object = SSD(get_only_param_val(2), get_only_param_val(4), get_only_param_val(5))
                            print_general_info()
                            print("\tKapacita [GB]: " + component_object.Capacity)
                            print("\tRychlost čtení [MB/s]: " + component_object.Speed_read)
                            print("\tRychlost zápisu [MB/s]: " + component_object.Speed_write)
                        elif compName == Search_enum.Motherboard:
                            # 2 = patice  4 = Čipová sada 5 = Formát základní desky
                            component_object = Motherboard(get_only_param_val(1), get_only_param_val(3), get_only_param_val(6))
                            print_general_info()
                            print("\tPatice: " + component_object.Patice)
                            print("\tČipová sada: " + component_object.Chipset)
                            print("\tFormát základní desky: " + component_object.Format)
                        elif compName == Search_enum.Procesor:
                            add_params_to_array(1)
                            # 1 = patice  14 = generace 2 = jádra 3 = počet vláken  4 = frekvence 5 = turbo 6 = tdp 12 = chipset
                            component_object = Procesor(get_only_param_val(0), get_only_param_val(14), get_only_param_val(2), get_only_param_val(3), get_only_param_val(4), get_only_param_val(5), get_only_param_val(6), get_only_param_val(12))

                            print("Kontroluji kompatibilitu: ")
                            if self.check_proc_compatibility_w_motherboard(component_object) == False:
                                continue

                            print_general_info()
                            print("\tPatice: " + component_object.Patice)
                            print("\tGenerace: " + component_object.Gen)
                            print("\tJádra: " + component_object.Cores)
                            print("\tPočet vláken: " + component_object.Threads)
                            print("\tFrekvence [MHz]: " + component_object.Frequenc)
                            print("\tTurbo [MHz]: " + component_object.Turbo)
                            print("\tTDP (W): " + component_object.Tdp)
                            print("\tChipset: " + component_object.Chipset)
                    except IndexError:
                        continue
                    except  TypeError:
                        continue
                        
                    component = Component(product_name, spec_page_url, iteration, price_final, compName, component_object)
                    componentsFound.append(component)
                print("Počet nalezených komponentů: " + str(len(componentsFound)))
        return componentsFound

    def choose_motherboard(self, motherboards):
        selected_motherboard_index = None
        while selected_motherboard_index == None:
            selected_motherboard_input = input("Vyber základovou desku (ID): ")
            if selected_motherboard_input.isnumeric() == False:
                print("Musíš zadat číslo")
            else:
                selected_motherboard_index = int(selected_motherboard_input)
                try:
                    self.selected_motherboard = [item for item in motherboards if item.ID == selected_motherboard_index][0]

                    print("Vybral si " + self.selected_motherboard.Product_name)
                    if input("Jsi si jistý? Y/N: ").lower() != "y":
                        selected_motherboard_index = None
                except IndexError:
                    print("Neexistuje základová deska s tímto ID")
                    selected_motherboard_index = None

    # Zatím pracuje pouze s CZC
    def hey_spock_beam_my_pc_up(self, how_many_products_compare):

        # vezmi všechny Základovky
        Motherboards = self.search_components_by_compName("https://www.czc.cz/", Search_enum.Motherboard, how_many_products_compare)

        # Vybereme motherboard
        self.choose_motherboard(Motherboards)
        
        Procesors = self.search_components_by_compName("https://www.czc.cz/", Search_enum.Procesor, how_many_products_compare)

        # Vezmi všechny SSD
        SSDs = self.search_components_by_compName("https://www.czc.cz/", Search_enum.SSD, how_many_products_compare)

        return ""