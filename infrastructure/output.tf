output "redshift_cluster_endpoint"{
    value = aws_redshift_cluster.default.endpoint
}

output "redshift_cluster_database_name"{
    value = aws_redshift_cluster.default.database_name
}

output "redshift_cluster_port"{
    value = aws_redshift_cluster.default.port
}

output "Redshift_IAM_Role" {
  value = aws_iam_role.redshift_role.arn
}