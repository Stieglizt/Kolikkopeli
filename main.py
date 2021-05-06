import pygame
from random import randint
# import time

class Kolikko_peli:
    
    #Kolikko ja robotti objektit
    class Kolikko:

        def __init__(self, spawn_x, spawn_y, nopeus=1):

            self.nopeus = nopeus
            self.tyyppi = 'kolikko'

            self.kuva = pygame.image.load('kolikko.png')
            self.rect = self.kuva.get_rect(center=(spawn_x,spawn_y))

        def siirra(self, y_muutos):
            self.rect.move_ip(0, y_muutos*self.nopeus)

    class Morko:

        def __init__(self, spawn_x, spawn_y, nopeus=2):

            self.nopeus = nopeus
            self.tyyppi = 'morko'

            self.kuva = pygame.image.load('hirvio.png')
            self.rect = self.kuva.get_rect(center=(spawn_x,spawn_y))

        def siirra(self, y_muutos):
            self.rect.move_ip(0, y_muutos*self.nopeus)

    class Robotti:

        def __init__(self, nopeus=5, y_rajoitus=0):
            
            self.nopeus = nopeus
            self.y_rajoitus = y_rajoitus

            self.kuva = pygame.image.load('robo.png')
            self.rect = self.kuva.get_rect(center=(320,437))

        #siirretään robotti ja katsotaan ettei se mene näytöstä ulos. Y rajoitus laitettu 300
        def siirra(self, x_muutos, y_muutos):
            if x_muutos == -1 and self.rect.left >= 0:
                self.rect.move_ip(x_muutos*self.nopeus, 0)
            if x_muutos == 1 and (self.rect.right+1) <= 640:
                self.rect.move_ip(x_muutos*self.nopeus, 0)
            if y_muutos == 1 and (self.rect.bottom+1) <= 480:
                self.rect.move_ip(0, y_muutos*self.nopeus)
            if y_muutos == -1 and self.rect.top >= self.y_rajoitus:
                self.rect.move_ip(0, y_muutos*self.nopeus)

    def __init__(self):

        #Alustetaan peli ja pelikello
        pygame.init()
        pygame.display.set_caption('KolikkoKeräys2077')
        pygame.display.set_icon(pygame.image.load('kolikko.png'))
        self.peli_kello = pygame.time.Clock()
        self.naytto = None
        self.kaynnissa = False
        self.alku = True
        self.lopetus = False

        #Peli luokan muuttujat
        #Pelaaja, tyhjät listat tippuville, todennäköisyydet, pisteet
        self.robotti = self.Robotti()
        self.kolikot = []
        self.morot = []
        self.ennatykset = []
        self.kolikon_todn = 50
        self.moron_todn = 25
        self.pisteet = 0
        self.moron_pisteet = 5
        self.kolikon_pisteet = 1
        self.fontti = pygame.font.SysFont('Comicsansms', 24) #Best game needs best font
        self.max_aika = 30
        self.aika_jaljella = self.max_aika
        self.vaikeus = None

        #Mahdolliset liikkeet robotille
        self.mahdolliset_liikeet = [
            (pygame.K_LEFT, -1, 0),
            (pygame.K_RIGHT, 1, 0),
            (pygame.K_UP, 0, -1),
            (pygame.K_DOWN, 0, 1)]

        #Muut komennot esim. vaikeus ja uusi peli
        self.muut_komennot = [
            (pygame.K_F1, 'Easy'),
            (pygame.K_F2, 'Normal'),
            (pygame.K_F3, 'Hard'),
            (pygame.K_F12, 'bonus'),
            (pygame.K_RETURN, None),
            (pygame.K_ESCAPE, None)]

        #pygamen nappaamat komennot reaaliajassa
        self.aktiiviset_komennot = {}

        #Luetaan ennätykset
        self.ennatykset = self.ennatykset_tiedostosta()

        #Pelin aloitus
        self.aloitus_kaynnissa()

    #Alustetaan pelin perusarvot alkuperäisiin uutta peliä varten
    def pelin_alustus(self):
        self.vaikeus = None
        self.pisteet = 0
        self.aika_jaljella = self.max_aika
        self.morot, self.kolikot = [], []

    #ladataan ennätykset tiedostosta Ja luodaan tiedosto jos tiedostoa ei löydy
    def ennatykset_tiedostosta(self):
        try:
            with open('ennatykset.txt', 'r') as ennatykset:
                return [int(ennatys.strip()) for ennatys in ennatykset]
        except FileNotFoundError:
            with open('ennatykset.txt', 'w') as t:
                pass
            return [0,0,0]

    #Tallennetaan ennatykset tiedostoon
    def tallenna_ennatykset(self):
        with open('ennatykset.txt', 'w') as tiedosto:
            for ennatys in self.ennatykset:
                tiedosto.write(f'{str(ennatys)}\n')

    #Piirretään aloitusnäyttö missä näkyy vaikeusasteet
    def piirra_aloitusnaytto(self):
        self.naytto.fill((0,0,0))
        tekstit = ['Easy [F1]','Normal [F2]','Hard [F3]']
        self.naytto.blit(self.fontti.render('TOP', True, (255,0,255)), (240, 30))
        for i in range(len(tekstit)):
            self.naytto.blit(self.fontti.render(tekstit[i], True, (255,0,255)), (20, (80+i*80)))
        for i in range(len(self.ennatykset)):
            self.naytto.blit(self.fontti.render(str(self.ennatykset[i]), True, (255,0,255)), (240, (80+i*80)))
        pygame.display.flip()

    #piirretään objekti pygame näyttöön
    def piirra(self, kuva, rect):
        self.naytto.blit(kuva, rect)

    #alapalkin piirtäminen pelinäyttöön. sisältää pisteet, vaikeusasteen ja ajan
    def piirra_alapalkki(self):
        pygame.draw.rect(self.naytto, (0,0,0),(0,480,640,50))
        pisteet = self.fontti.render(f'Pisteet: {self.pisteet}', True, (255,0,255))
        aika = self.fontti.render(f'Aika: {self.aika_jaljella}', True, (255,0,255))
        vaikeus = self.fontti.render(f'{self.vaikeus}', True, (255,0,255))
        self.naytto.blit(vaikeus, (300,480+(50-pisteet.get_height())/2))
        self.naytto.blit(pisteet, (20,480+(50-pisteet.get_height())/2))
        self.naytto.blit(aika, (530,480+(50-pisteet.get_height())/2))
  
    #Piirretään näyttö ja flipataan pygameen
    def piirra_pelinaytto(self):
        self.naytto.fill((255,255,255))
        self.piirra_alapalkki()
        self.piirra(self.robotti.kuva, self.robotti.rect)
        for kolikko in self.kolikot:
            self.piirra(kolikko.kuva, kolikko.rect)
        for morko in self.morot:
            self.piirra(morko.kuva, morko.rect)
        pygame.display.flip()

    #Piirretään lopetusteksti ja pisteet
    def piirra_lopetus(self):
        tekstit = ['Peli päättyi!', f'Sait {self.pisteet} pistettä', 'Uusi peli? [ENTER]']
        for i in range(len(tekstit)):
            rivi = self.fontti.render(tekstit[i], True, (255,0,255))
            self.naytto.blit(rivi, (320-rivi.get_width()/2, (215-rivi.get_height()/2)+i*50))
        pygame.display.flip()

    #asetetaan vaikeus pelille
    def vaikeuden_valinta(self):
        for komento in self.muut_komennot[0:5]:
            if komento[0] in self.aktiiviset_komennot:
                self.vaikeus = komento[1]

    #Vaikeusasteen perusteella tehdään pelin muuttujiin muutoksia
    def vaikeuden_alustus(self):
        if self.vaikeus == 'Easy':
            self.kolikon_todn = 60
            self.moron_todn = 25
        if self.vaikeus == 'Normal':
            self.kolikon_todn = 60
            self.moron_todn = 60
        if self.vaikeus == 'Hard':
            self.kolikon_todn = 60
            self.moron_todn = 85
        if self.vaikeus == 'bonus':
            self.robotti = self.Robotti(15)
            self.kolikon_todn = 500
            self.moron_todn = 0

    #Tarkastetaan komento ENTER
    def lopetus_valinta(self):
        for komento in self.muut_komennot:
            if komento[0] in self.aktiiviset_komennot:
                if komento[0] == pygame.K_RETURN:
                    self.alku = True

    #Tarkastetaan onko pisteet enemmän kuin vastaavan vaikeusasteen ennätys. typerällä if-rakenteella koska halusin käyttää 
    #vaikeusasteissa str muotoa muiden funktioiden käsittelyn helpottamiseksi
    def tuliko_ennatys(self):
        if self.vaikeus == 'Easy':
            if self.pisteet > self.ennatykset[0]:
                self.ennatykset[0] = self.pisteet
        if self.vaikeus == 'Normal':
            if self.pisteet > self.ennatykset[1]:
                self.ennatykset[1] = self.pisteet
        if self.vaikeus == 'Hard':
            if self.pisteet > self.ennatykset[2]:
                self.ennatykset[2] = self.pisteet

    #luodaan kolikko ja morko listaan X-prosentin todennäköisyydellä
    def luo_kolikko(self):
        if randint(1,1000) <= self.kolikon_todn:
            self.kolikot.append(self.Kolikko(randint(20,620), -20))
    def luo_morko(self): 
        if randint(1,1000) <= self.moron_todn:
            self.morot.append(self.Morko(randint(20,620), -20))

    #Siirrot robotille komentojen mukaan ja kolikot ja möröt tippuvat tasaisesti nopeuden mukaan
    def robotin_liikutus(self):
        for komento in self.mahdolliset_liikeet:
            if komento[0] in self.aktiiviset_komennot:
                self.robotti.siirra(komento[1],komento[2])

    #liikutetaan esineita alaspäin ja jos esine on lattiassa niin poistetaan listasta oikean tyypin mukaan
    def tippuvan_esineen_liikutus(self, esine):
        if esine.rect.bottom+1 == 480:
            if esine.tyyppi == 'kolikko':
                self.kolikot.remove(esine)
            if esine.tyyppi == 'morko':
                self.morot.remove(esine)
        esine.siirra(esine.nopeus)

    #Tutkitaan törämykset rectangle-objektien välillä collide funktiolla joka löytyy pygamesta
    def tutki_tormaykset(self, esine):
        if esine.rect.colliderect(self.robotti.rect):
            if esine.tyyppi == 'kolikko':
                self.kolikot.remove(esine)
                self.pisteet += self.kolikon_pisteet
            if esine.tyyppi == 'morko':
                self.morot.remove(esine)
                self.pisteet -= self.moron_pisteet
        
    #Haetaan pygameen näppäinkomennot ja lisätään komento dictionaryyn
    def komentojen_tarkastus(self):
        for tapahtuma in pygame.event.get():

            #lisätään tapahtumat dictionaryyn painettaessa näppäin alas
            if tapahtuma.type == pygame.KEYDOWN:
                self.aktiiviset_komennot[tapahtuma.key] = True

            #poistetaan tapahtumat dictionaryyn näppäimen noustessa
            if tapahtuma.type == pygame.KEYUP:
                del self.aktiiviset_komennot[tapahtuma.key]

            if tapahtuma.type == pygame.QUIT:
                self.tallenna_ennatykset()
                exit()

    #Aikalaskuri aloitus-ajasta
    def ajastin(self, aloitus_aika):
        self.aika_jaljella = self.max_aika-(pygame.time.get_ticks()-aloitus_aika)//1000
        if self.aika_jaljella <=0:
            self.aika_jaljella = 0

    #Aloitus ruudun silmukka
    def aloitus_kaynnissa(self):
        self.pelin_alustus()
        self.naytto = pygame.display.set_mode((340, 320))
        while self.alku:
            self.piirra_aloitusnaytto()
            self.komentojen_tarkastus()
            self.vaikeuden_valinta()
            self.vaikeuden_alustus()
            if self.vaikeus != None:
                self.alku = False
                self.kaynnissa = True
                self.peli_kaynnissa()

    #Aika loppui silmukka joka tulostaa tekstin ja pisteet. 
    #Enter komento vie takaisin aloitusnäyttöön ja uuden pelin aloitukseen
    def aika_loppui(self):
        self.kaynnissa = False
        self.lopetus = True
        while self.lopetus:
            self.piirra_lopetus()
            self.komentojen_tarkastus()
            self.lopetus_valinta()
            if self.alku:
                self.aloitus_kaynnissa()

    #Pelin silmukka
    def peli_kaynnissa(self):

        #Alustetaan näyttö ja otetaan aloitusaika
        self.naytto = pygame.display.set_mode((640, 530))
        aloitus_aika = pygame.time.get_ticks()

        #pelin pääsilmukka
        while self.kaynnissa:

            #Pelin päivitysnopeus
            self.peli_kello.tick(60)

            #Luodaan kolikot ja hirviöt sattumanvaraisesti
            self.luo_kolikko()
            self.luo_morko()

            #tarkastetaan painallukset, minkä jälkeen liikutetaan robottia
            self.komentojen_tarkastus()
            self.robotin_liikutus()

            #liikutetaan kolikoita ja tarkastetaan osuiko robottiin
            for kolikko in self.kolikot:
                self.tutki_tormaykset(kolikko)

                #Bugin korjaus jos esine osuu sopivasti lattiaan ja robottiin tulee listavirhe liikutusfunktiossa
                if kolikko in self.kolikot:
                    self.tippuvan_esineen_liikutus(kolikko)
            for morko in self.morot:
                self.tutki_tormaykset(morko)
                if morko in self.morot:
                    self.tippuvan_esineen_liikutus(morko)   

            #Ajan tarkistus ja vähennys
            self.ajastin(aloitus_aika)
            
            #Piirretään kaikki näytölle
            self.piirra_pelinaytto()

            #Kun aika loppuu peli päättyy ja mennään odotussilmukkaan odottamaan uutta komentoa
            if self.aika_jaljella <= 0:
                self.tuliko_ennatys()
                self.aika_loppui()

Kolikko_peli()