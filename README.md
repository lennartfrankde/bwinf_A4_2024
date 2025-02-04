

# Aufgabe 4: Krocket

##### Team-ID: 00219

##### Team: Team

##### Bearbeiter/-innen dieser Aufgabe:
##### Lennart Frank

##### 15. November 2024

### Inhalt

[Inhalt 1](#_Toc182587659)

[Lösungsidee 1](#_Toc182587660)

[Interpretation der Aufgabenstellung 1](#_Toc182587661)

[Rechenansatz 2](#_Toc182587662)

[Umsetzung 2](#_Toc182587663)

[Python 2](#_Toc182587664)

[Einlesen der Daten 2](#_Toc182587665)

[Berechnung des Vektors 2](#_Toc182587666)

[Darstellung der Ergebnisse 3](#_Toc182587667)

[Rust 3](#_Toc182587668)

[Optimierung 3](#_Toc182587669)

[Ergebnisse der Optimierung 3](#_Toc182587670)

[Beispiele 4](#_Toc182587671)

[Beispiel 1 4](#_Toc182587672)

[Beispiel 2 5](#_Toc182587673)

[Beispiel 3 5](#_Toc182587674)

[Beispiel 4 6](#_Toc182587675)

[Beispiel 5 6](#_Toc182587676)

# Lösungsidee

## Interpretation der Aufgabenstellung

Als erstes habe ich die Aufgabenstellung untersucht, um diese in greifbarere Ziele zu unterteilen, dabei habe ich die Annahme getroffen, dass die Tore als Strecken in einem zweidimensionalen Koordinatensystem dargestellt werden können, sowie dass der Ball auf einer weiteren Strecke rollt. Um dessen Radius darzustellen habe ich den Durchmesser als Zwei um den Radius verschobene Strecken dargestellt.

## Rechenansatz

Als Rechenansatz habe ich mir überlegt verschiedene Strecken mit einem Start und Endpunkt auf dem ersten und letzten Tor auszuprobieren und die Anzahl durchkreuzter Tore zu zählen. Dann nimmt man den Besten Wert davon und hat den Besten Schlag im von uns betrachteten Bereich.

# Umsetzung

## Python

### Einlesen der Daten

Als erstes habe ich die Datei geöffnet, und alle Punkte in einen Array geschrieben. Wenn es das Beispiel Krocket 3 war, habe ich noch zusätzlich die Daten sortiert, da sonst mein Algorithmus nicht funktioniert. Außerdem habe ich den Radius zu einem Durchmesser umgerechnet und diese Daten zurückgegeben.

### Berechnung des Vektors

Um den Vektor zu berechnen, Starte ich damit eine Geringe Anzahl and Start und Endpunkten basierend auf der ersten und letzten Strecke zu generieren. (Dies dient der Laufzeitoptimierung später mehr dazu)

Anschließend wird Brute Force mäßig für alle Start und Endpunkte kombiniert zu Zählen wie viele Tore gekreuzt werden.

Um dies zu Zählen erstelle ich mir basierend auf Start und Endpunkt zwei parallele Strecken, welche die Breite des Balles darstellen sollen. Diese erweitere ich dann noch, da durch die Verschiebung sonst die Strecken zu kurz sind, um die erste zu kreuzen.

Dann gehe ich einfach alle Tore durch und prüfe, ob die getestete Strecke durch das Tor kreuzen kann, indem ich ihre Orientation prüfe und zusätzlich noch prüfe, ob sich ihre Definitionsbereiche treffen.

Zuletzt muss ich nur noch Prüfen welcher der Vektoren die meisten Schnittpunkte hat. Wenn nun nicht alle Tore gekreuzt wurden, Teste ich mehr Punkte auf der Strecke, bis ich mein Maximum an Punkten erreicht habe. Durch diese Vorgehensweise kann ich die Laufzeit des Programms auf ca. 60 Sekunden für alle Beispiele Zusammen auf meinem Rechner reduzieren. Ohne diese Optimierung würde der Code ca. 93 Sekunden Brauchen.

### Darstellung der Ergebnisse

Um die Ergebnisse Anschaulich darzustellen, erstelle ich mithilfe einer Grafikbibliothek .svg Dateien um die Tore sowie den Schlag darzustellen. Außerdem gebe ich noch den Start und Endpunkt sowie eine Gleichung an.

## Rust

### Optimierung

Da ich mit der Laufzeit des Programmes unzufrieden war, habe ich mich dazu entschieden mein Python Code als Prototypen zu nehmen und diesen in Rust nachzustellen. Dadurch konnte ich nicht nur die Laufzeit drastisch verbessern, sondern auch die Problematik lösen, dass die richtigen Bibliotheken sowie Python Version installiert sein müssen, um das Programm auszuführen.

### Ergebnisse der Optimierung

Durch die Implementierung in Rust konnte ich die Laufzeit der Berechnung aller Beispiele infolge von ca. 60 Sekunden auf ca. 800ms reduzieren.

# Beispiele

## Beispiel 1

Start (11.285714285714286, 9.071428571428571),

End (238.57142857142858, 120.71428571428572)

Crossed Gates: 9 out of 9

![](data:image/png;base64...)

# Beispiel 2

Start (11.850746268656717, 4.26865671641791),

End (243.12686567164178, 218.87313432835822)

Crossed Gates: 8 out of 9

* Nicht mit einem (Geraden) Schlag möglich

![](data:image/png;base64...)

## Beispiel 3

Start (22.714285714285715, 126.78571428571429),

End (31628.5, 127.92857142857144)

Crossed Gates: 396 out of 396

![](data:image/png;base64...)

## Beispiel 4

Start (6.138297872340425, 181.84042553191466),

End (8946.531914893618, 4672.063829787234)

Crossed Gates: 344 out of 344

Graph kann des Platzes halber im Verzeichnis gefunden werden.

## Beispiel 5

Start (1317.0, 14680.702127659575),

End (48839.85106382979, 2761.0638297872338)

Crossed Gates: 406 out of 406

Graph kann des Platzes halber im Verzeichnis gefunden werden.
