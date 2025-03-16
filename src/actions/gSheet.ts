


const API_KEY = process.env.SHEETS_API;
const SPREADSHEET_ID = process.env.SHEETS_ID;

export async function getSheetData(sheetName:string, range) {
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/${sheetName}!${range}?key=${API_KEY}`;
  try {
    const response = await axios.get(url);
    return response.data.values;
  } catch (error) {
    console.error('Error fetching data:', error);
    return null;
  }
}