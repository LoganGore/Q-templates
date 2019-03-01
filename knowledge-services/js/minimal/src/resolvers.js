/*===============================================================================
 copyright 2018 Maana Incorporated
 Released under the MIT License.

 Permission is hereby granted, free of charge, to any person obtaining a copy of 
 this software and associated documentation files (the "Software"), to deal in 
 the Software without restriction, including without limitation the rights to use, 
 copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the 
 Software, and to permit persons to whom the Software is furnished to do so, 
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all 
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
 SOFTWARE.
=============================================================================*/
const crypto = require('crypto');
require('dotenv').config()                      // load .env into process.env.*

module.exports = {
  Query: {
    // The info query must be provided to ensure proper registration of 
    // a service with the maana platform
    info: async () => {
      return {
        id: `${crypto.createHash('md5').update(process.env.SERVICE_ID).digest('hex')}`,
        name: process.env.SERVICE_ID,
        description: process.env.DESCRIPTION,
        srl: process.env.SRL
      }
    },
    // ADD CUSTOM RESOLVERS HERE.
    getName: async (root,{ input }) => { return input.name },
    getID: async (root,{ input }) => { return input.id },
    getSpan: async (root,{ input }) => { return input.span },
    getOffset: async (root,{ input }) => { return input.offset },
    getSurfaceForm: async (root,{ input }) => { return input.surfaceForm },
    getMagnitude: async (root,{ input }) => { return input.magnitude },
    getEntity: async (root, {input} ) => { return input.entity }
  }
}