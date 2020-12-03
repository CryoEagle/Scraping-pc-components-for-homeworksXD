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

class Component:
    def __init__(self, name, url, id, price, comp_name, comp_obj):
        self.Price = price
        self.Comp_name = comp_name
        self.Comp_obj = comp_obj
        self.Url = url
        self.ID = id
        self.Product_name = name

selected_motherboard = None

def search_components_by_compName(pageUrl, compName, how_many_products_fetch, architectureType = "all"):
    print("vyhledávám: " + compName)

    componentsFound = []

    iteration = 0
    last_page = 0

    if pageUrl == "https://www.czc.cz/":
        page = requests.get(pageUrl + compName + "/hledat") # stránka s produkty
        soup = BeautifulSoup(page.content, 'html.parser') # parsnutí do zpracovatelné formy

        job_elems = soup.find_all('div', class_='new-tile') # vezmeme array produktů (html element)
        
        print("dosažený počet produktů: " + str(len(job_elems)))
        
        if len(job_elems) > how_many_products_fetch:
            print("Přesažený počet produktů - zkracuji")
            for i in range(0, len(job_elems) - how_many_products_fetch): 
                job_elems.pop()

        while len(job_elems) < how_many_products_fetch:
            print("nedosažený počet potřebných produktů, opakuji request")
            another_page = requests.get(pageUrl + compName + "/hledat?q-first=" + str(len(job_elems)))
            soup_another_page = BeautifulSoup(another_page.content, 'html.parser')
            job_elems_another_page = soup.find_all('div', class_='new-tile')
            for job_elem in job_elems_another_page:
                if len(job_elems) < how_many_products_fetch:
                    job_elems.append(job_elem)
                else:
                    print("dosažený počet produktů: " + str(len(job_elems)))
                    break

        print("\r\nSbírám specifikace " + compName)

        for job_elem in job_elems: # projíždíme produkty
            iteration += 1
            product_name = job_elem.find(class_ = "tile-title").text
            url_to_specifications = job_elem.find(class_ = "tile-link") # vyhledáme odkaz na produkt
            url_to_specifications = url_to_specifications.get("href") # vezmeme hodnotu attributu href
            
            spec_page_url = pageUrl + url_to_specifications[1:] # stránka se specifikací
            spec_page = requests.get(spec_page_url) # pošleme request
            soup_spec = BeautifulSoup(spec_page.content, 'html.parser') # parsneme do zpracovatelné formy

            # cena
            price = soup_spec.find(class_ = "total-price") # najdeme cenu
            price_final = str(price.find(class_ = "price-vatin").text) # vezmeme text uvnitř komponentu s cenou

            # další parametry
            params = soup_spec.find(class_ = "pd-parameter-item") # vezmeme element obsahující všechny technický parametry

            # extrakce parametrů do array
            paramsArray = []

            # technické parametry
            first_param = params.find("p") # vezmeme první parametr
            paramsArray.append(first_param) # přidáme do array parametrů
            first_param_siblings = first_param.find_next_siblings("p") # vezmeme všechny sousedící parametry s prvním parametrem
            for sibling in first_param_siblings: # sousedící parametry iterujeme a přidáme do array parametrů
                paramsArray.append(sibling)

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
                print("\tOdkaz: " + spec_page_url)
                print("\tCena: " + price_final)


            if compName == Search_enum.SSD:
                # 2 = kapacita  4 = rychlost čtení 5 = rychlost zápisu
                component_object = SSD(get_only_param_val(2), get_only_param_val(4), get_only_param_val(5))
                print_general_info()
                print("\tKapacita [GB]: " + component_object.Capacity)
                print("\tRychlost čtení [MB/s]: " + component_object.Speed_read)
                print("\tRychlost zápisu: [MB/s]" + component_object.Speed_write)
            elif compName == Search_enum.Motherboard:
                try:
                    # 2 = patice  4 = Čipová sada 5 = Formát základní desky
                    component_object = Motherboard(get_only_param_val(1), get_only_param_val(3), get_only_param_val(6))
                    print_general_info()
                    print("\tPatice: " + component_object.Patice)
                    print("\tČipová sada: " + component_object.Chipset)
                    print("\tFormát základní desky: " + component_object.Format)
                except IndexError:
                    continue
                except  TypeError:
                    continue
            component = Component(product_name, spec_page_url, iteration, price_final, compName, component_object)
            componentsFound.append(component)

        return componentsFound

def compare_products():

    return ""

# Zatím pracuje pouze s CZC
def hey_spock_beam_my_pc_up(how_many_products_compare):
    selected_motherboard_index = None


    # vezmi všechny Základovky
    Motherboards = search_components_by_compName("https://www.czc.cz/", Search_enum.Motherboard, how_many_products_compare)

    # Vybereme motherboard
    while selected_motherboard_index == None:
        selected_motherboard_input = input("Vyber základovou desku (index): ")
        if selected_motherboard_input.isnumeric() == False:
            print("Musíš zadat číslo")
        else:
            selected_motherboard_index = int(selected_motherboard_input)
            try:
                selected_motherboard = [item for item in Motherboards if item.ID == selected_motherboard_index]
                print("Vybral si " + selected_motherboard[0].Product_name)
            except IndexError:
                print("Na tomto indexu se žádná základovka nenachází")
                selected_motherboard_index = None
    
    Procesors = search_components_by_compName("https://www.czc.cz/", Search_enum.Procesor, how_many_products_compare)

    # Vezmi všechny SSD
    SSDs = search_components_by_compName("https://www.czc.cz/", Search_enum.SSD, how_many_products_compare)

    return ""