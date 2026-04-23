import bcrypt from 'bcryptjs'

export const generatePasswordHash = async (password) => {
  const saltRounds = 10
  return await bcrypt.hash(password, saltRounds)
}