object MissingNumberApp {
  def main(args: Array[String]): Unit = {
    if (args.length != 1) {
      println("Por favor introduce 1 número para extraer (1-100)")
      sys.exit(1)
    }

    val numberToExtract = try {
      args(0).toInt
    } catch {
      case _: NumberFormatException =>
        println("Error: Debes introducir un número válido.")
        sys.exit(1)
    }

    if (numberToExtract < 1 || numberToExtract > 100) {
      println("Error: El número debe estar entre 1 y 100.")
      sys.exit(1)
    }

    val numberSet = new NumberSet()
    numberSet.extract(numberToExtract)
    val missing = numberSet.findMissing()

    println(s"El número que falta es: $missing")
  }
}

class NumberSet {
  private var numbers: List[Int] = (1 to 100).toList

  def extract(n: Int): Unit = {
    if (!numbers.contains(n)) {
      println(s"El número $n no está en el conjunto.")
      sys.exit(1)
    }
    numbers = numbers.filter(_ != n)
  }

  def findMissing(): Int = {
    val expectedSum = 100 * 101 / 2  // Suma de 1..100
    val actualSum = numbers.sum
    expectedSum - actualSum
  }
}

