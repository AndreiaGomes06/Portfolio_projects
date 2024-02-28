# Query all the elements from coviddeaths
SELECT *
FROM project_covid.coviddeaths
WHERE continent is not null
ORDER BY 3,4;

SELECT location, date, total_cases, new_cases, total_deaths, population
FROM project_covid.coviddeaths
WHERE continent is not null
ORDER BY 1,2;

#Total cases vs. total deaths - shows the percentage of deaths within the infected people in Algeria
SELECT location, date, total_cases, total_deaths, round((total_deaths/total_cases)*100, 2) as Death_percentage
FROM project_covid.coviddeaths
WHERE location like 'Afghanistan'
ORDER BY 1,2;

#Total cases vs. population - shows the percentage of the population that got covid
SELECT location, date, total_cases, population, round((total_cases/population)*100, 2) as Population_infected_per
FROM project_covid.coviddeaths
WHERE location like 'Afghanistan'
ORDER BY 1,2;

#Highest Infection cases and Highets percentage of infected population order by the percentage
SELECT location, population, MAX(total_cases) as Highest_infection_cases, MAX(round((total_cases/population)*100, 2)) as Population_infected_per
FROM project_covid.coviddeaths
WHERE continent is not null
GROUP BY location, population
ORDER BY Population_infected_per desc;

#Highest number of deaths
SELECT location, population, MAX(cast(total_deaths as UNSIGNED)) as Total_deaths
FROM project_covid.coviddeaths
WHERE continent is not null
GROUP BY location, population
ORDER BY Total_deaths desc;

#Contenents with the highest number of deaths per population
SELECT continent, population, MAX(cast(total_deaths as UNSIGNED)) as Total_deaths
FROM project_covid.coviddeaths
WHERE continent is not null
GROUP BY continent
ORDER BY Total_deaths desc;

#Total cases, and total deaths and death percentage by day in the entire world 
SELECT  date, SUM(new_cases) as total_cases, SUM(cast(new_deaths as UNSIGNED)) as total_deaths, SUM(cast(new_deaths as UNSIGNED))/SUM(new_cases)*100 as death_per
FROM project_covid.coviddeaths
WHERE continent is not null
GROUP BY date
ORDER BY 1,2;

#Total cases, and total deaths and death percentage in the entire world 
SELECT  SUM(new_cases) as total_cases, SUM(cast(new_deaths as UNSIGNED)) as total_deaths, SUM(cast(new_deaths as UNSIGNED))/SUM(new_cases)*100 as death_per
FROM project_covid.coviddeaths
WHERE continent is not null
ORDER BY 1,2;

# Query all the elements from covidvaccination
SELECT *
FROM project_covid.covidvaccinations
GROUP BY 3,4;

#Join both tables
SELECT *
FROM project_covid.coviddeaths dea
JOIN project_covid.covidvaccinations vac
on dea.location = vac.location
and dea.date = vac.date;

#Total population vs. new vaccination per day                                                                                      
SELECT dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(convert(vac.new_vaccinations, UNSIGNED))
#parte por localização, cada localização tem a sua contagem
 OVER (partition by dea.location order by dea.location, dea.date) as added_vaccins
FROM project_covid.coviddeaths dea
JOIN project_covid.covidvaccinations vac
	on dea.location = vac.location
	and dea.date = vac.date
order by 2,3;

#We want to use the added_vaccins to perform calculations so we have to create a CTE- common table expression (CTE) is a named temporary 
#result set that exists within the scope of a single statement and that can be referred to later within that statement, possibly multiple times
#Give us the percentage of the population in each location that is vaccinated
with popvsvac (continent, location, date,  population, new_vaccinations, added_vaccins)
AS (
SELECT  dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(convert(vac.new_vaccinations, UNSIGNED))
 OVER (partition by dea.location order by dea.location, dea.date) as added_vaccins
FROM project_covid.coviddeaths dea
JOIN project_covid.covidvaccinations vac
	on dea.location = vac.location
	and dea.date = vac.date
) SELECT *, (added_vaccins/population) * 100
FROM popvsvac;

#If the query is simple and does not require the use of complex logic, then a CTE may be the best option.
# However, if the query is complex or requires the use of large amounts of data, then a TempTable may be the better choice.

#Creating a view to store data
CREATE View deathsforpopulation as
SELECT continent, population, MAX(cast(total_deaths as UNSIGNED)) as Total_deaths
FROM project_covid.coviddeaths
WHERE continent is not null
GROUP BY continent
ORDER BY Total_deaths desc;

SELECT * FROM deathsforpopulation;

#Create a view for the total cases, and total deaths and death percentage in the entire world 
Create View totalcasesdeathsandper as
SELECT  SUM(new_cases) as total_cases, SUM(cast(new_deaths as UNSIGNED)) as total_deaths, SUM(cast(new_deaths as UNSIGNED))/SUM(new_cases)*100 as death_per
FROM project_covid.coviddeaths
WHERE continent is not null
ORDER BY 1,2;

SELECT * FROM totalcasesdeathsandper;