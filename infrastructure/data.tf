
data "aws_iam_policy_document" "redshift_assume_role"{
 statement {
    actions = ["sts:AssumeRole"]
    effect = "Allow"
    principals {
          type = "Service"
          identifiers = [ "redshift.amazonaws.com" ]
    }
 }
}


data "aws_iam_policy_document" "public_read_access" {
  statement {
	  effect  = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      "arn:aws:s3:::${var.s3_udacity_bucket}",
      "arn:aws:s3:::${var.s3_udacity_bucket}/*",
    ]
  }
}